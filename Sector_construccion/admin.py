from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

# --------------------------
# Función auxiliar para traer el valor del total según tipo_dato
# --------------------------
def get_model_total_construccion(mes, anio, valor, tipo_dato):
    qs = SectorConstruccion.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor
    ).values("total_puesto_trabajo", "salario_promedio").first()

    if not qs:
        return None

    if tipo_dato == 1:  # puestos de trabajo
        return qs["total_puesto_trabajo"]
    elif tipo_dato == 2:  # salario promedio
        return qs["salario_promedio"]

    return None

# --------------------------
# Función principal para calcular y guardar variación
# --------------------------
def calcular_y_guardar_variacion(obj, tipo_dato, campo_valor):
    data_indicadores = {
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'total': getattr(obj, campo_valor)
    }

    anio_anterior = int(data_indicadores['anio_id']) - 1

    # --- Lógica intermensual
    if data_indicadores['mes_id'] == 1:
        mes_anterior = 12
        anio_anterior_intermensual = anio_anterior
    else:
        mes_anterior = int(data_indicadores['mes_id']) - 1
        anio_anterior_intermensual = data_indicadores['anio_id']

    data_intermensual = get_model_total_construccion(
        mes=mes_anterior,
        anio=anio_anterior_intermensual,
        valor=data_indicadores['valor_id'],
        tipo_dato=tipo_dato
    )

    # --- Lógica interanual
    data_interanual = get_model_total_construccion(
        mes=data_indicadores['mes_id'],
        anio=anio_anterior,
        valor=data_indicadores['valor_id'],
        tipo_dato=tipo_dato
    )

    var_intermensual = 0.0
    var_interanual = 0.0

    if data_intermensual and float(data_intermensual) != 0:
        var_intermensual = (float(data_indicadores['total']) / float(data_intermensual)) * 100 - 100

    if data_interanual and float(data_interanual) != 0:
        var_interanual = (float(data_indicadores['total']) / float(data_interanual)) * 100 - 100

    # Guardar en Indicadores
    Indicadores.objects.update_or_create(
        anio=obj.anio,
        mes=obj.mes,
        valor=obj.valor,
        tipo_dato_id=tipo_dato,
        defaults={
            "variacion_intermensual": round(var_intermensual, 1) if var_intermensual is not None else None,
            "variacion_interanual": round(var_interanual, 1) if var_interanual is not None else None,
        }
    )

# --------------------------
# Signal para recalcular automáticamente
# --------------------------
@receiver(post_save, sender=SectorConstruccion)
def sector_construccion_post_save(sender, instance, created, **kwargs):
    # Definir mapeo de campos con tipo_dato (solo 1 y 2)
    campos_tipo_dato = {
        1: "total_puesto_trabajo",
        2: "salario_promedio",
    }

    # Recalcula la variación del objeto actual
    for tipo_dato, campo_valor in campos_tipo_dato.items():
        calcular_y_guardar_variacion(instance, tipo_dato, campo_valor)

    # Recalcula el mes siguiente
    if instance.mes.id == 12:
        next_month_obj = SectorConstruccion.objects.filter(
            anio_id=instance.anio.id + 1,
            mes_id=1,
            valor_id=instance.valor.id
        ).first()
    else:
        next_month_obj = SectorConstruccion.objects.filter(
            anio_id=instance.anio.id,
            mes_id=instance.mes.id + 1,
            valor_id=instance.valor.id
        ).first()

    if next_month_obj:
        for tipo_dato, campo_valor in campos_tipo_dato.items():
            calcular_y_guardar_variacion(next_month_obj, tipo_dato, campo_valor)

    # Recalcula el mismo mes del año siguiente
    next_year_obj = SectorConstruccion.objects.filter(
        anio_id=instance.anio.id + 1,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id
    ).first()

    if next_year_obj:
        for tipo_dato, campo_valor in campos_tipo_dato.items():
            calcular_y_guardar_variacion(next_year_obj, tipo_dato, campo_valor)

# --------------------------
# Admin
# --------------------------
@admin.register(SectorConstruccion)
class SectorConstruccionAdmin(admin.ModelAdmin):
    search_fields = ['anio__anio','mes__mes','valor__valor']
    list_filter = ['anio__anio','mes__mes','valor__valor']
    ordering = ['-anio','mes']
    list_display = ['anio','mes','valor','total_empresas','total_puesto_trabajo','salario_promedio']
    list_editable = ['total_empresas','total_puesto_trabajo','salario_promedio']
    list_per_page = 12

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(Indicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    search_fields = ['anio__anio','mes__mes','valor__valor']
    list_filter = ['anio__anio','mes__mes','valor__valor']
    ordering = ['-anio','mes']
    list_display = ['anio','mes','valor','tipo_dato','variacion_interanual','variacion_intermensual']
    list_editable = ['mes','valor','tipo_dato','variacion_interanual','variacion_intermensual']
    list_per_page = 12
