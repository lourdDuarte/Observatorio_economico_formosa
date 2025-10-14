from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

# Función para obtener un registro específico
def get_indicador_data(mes, anio, valor, movimiento, tipo_vehiculo):
    return Indicadores.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        movimiento_vehicular_id=movimiento,
        tipo_vehiculo_id=tipo_vehiculo
    ).first()

# --- Cálculos principales ---
def calcular_valores(obj):
    total_actual = int(obj.total)
    mes_actual = obj.mes.id
    anio_actual = obj.anio.id

    # --- Total Acumulado ---
    total_acumulado = total_actual
    if mes_actual > 1:
        indicador_anterior = get_indicador_data(
            mes=mes_actual - 1,
            anio=anio_actual,
            valor=obj.valor.id,
            movimiento=obj.movimiento_vehicular.id,
            tipo_vehiculo=obj.tipo_vehiculo.id
        )
        if indicador_anterior and indicador_anterior.total_acumulado:
            total_acumulado += int(indicador_anterior.total_acumulado)

    # --- Variación Intermensual ---
    var_intermensual = 0.0
    if mes_actual == 1:
        mes_anterior_intermensual = 12
        anio_anterior_intermensual = anio_actual - 1
    else:
        mes_anterior_intermensual = mes_actual - 1
        anio_anterior_intermensual = anio_actual

    data_intermensual = get_indicador_data(
        mes=mes_anterior_intermensual,
        anio=anio_anterior_intermensual,
        valor=obj.valor.id,
        movimiento=obj.movimiento_vehicular.id,
        tipo_vehiculo=obj.tipo_vehiculo.id
    )
    if data_intermensual and int(data_intermensual.total) != 0:
        var_intermensual = (total_actual / int(data_intermensual.total)) * 100 - 100

    # --- Variación Interanual ---
    var_interanual = 0.0
    anio_anterior_interanual = anio_actual - 1
    data_interanual = get_indicador_data(
        mes=mes_actual,
        anio=anio_anterior_interanual,
        valor=obj.valor.id,
        movimiento=obj.movimiento_vehicular.id,
        tipo_vehiculo=obj.tipo_vehiculo.id
    )
    if data_interanual and int(data_interanual.total) != 0:
        var_interanual = (total_actual / int(data_interanual.total)) * 100 - 100

    return {
        'total_acumulado': str(total_acumulado),
        'variacion_intermensual': str(round(var_intermensual, 1)) if var_intermensual is not None else None,
        'variacion_interanual': str(round(var_interanual, 1)) if var_interanual is not None else None,
    }

# --- Signal ---
@receiver(post_save, sender=Indicadores)
def indicadores_post_save_handler(sender, instance, **kwargs):
    # Recalcular el actual
    valores_actuales = calcular_valores(instance)
    Indicadores.objects.filter(pk=instance.pk).update(
        total_acumulado=valores_actuales['total_acumulado'],
        variacion_intermensual=valores_actuales['variacion_intermensual'],
        variacion_interanual=valores_actuales['variacion_interanual']
    )

    # --- Recalcular todos los posteriores del mismo año ---
    posteriores = Indicadores.objects.filter(
        anio=instance.anio,
        valor=instance.valor,
        movimiento_vehicular=instance.movimiento_vehicular,
        tipo_vehiculo=instance.tipo_vehiculo,
        mes__id__gt=instance.mes.id
    ).order_by('mes__id')

    acumulado = int(valores_actuales['total_acumulado'])
    for indicador in posteriores:
        acumulado += int(indicador.total)
        valores = calcular_valores(indicador)
        valores['total_acumulado'] = str(acumulado)
        Indicadores.objects.filter(pk=indicador.pk).update(
            total_acumulado=valores['total_acumulado'],
            variacion_intermensual=valores['variacion_intermensual'],
            variacion_interanual=valores['variacion_interanual']
        )

    # --- También recalcular el mismo mes del año siguiente ---
    siguiente_anio = get_indicador_data(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        valor=instance.valor.id,
        movimiento=instance.movimiento_vehicular.id,
        tipo_vehiculo=instance.tipo_vehiculo.id
    )
    if siguiente_anio:
        valores_siguiente_anio = calcular_valores(siguiente_anio)
        Indicadores.objects.filter(pk=siguiente_anio.pk).update(
            total_acumulado=valores_siguiente_anio['total_acumulado'],
            variacion_intermensual=valores_siguiente_anio['variacion_intermensual'],
            variacion_interanual=valores_siguiente_anio['variacion_interanual']
        )

# --- Admin ---
@admin.register(Indicadores)
class PatentamientoIndicadorAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'movimiento_vehicular', 'tipo_vehiculo__tipo_vehiculo', 'valor__valor']
    search_fields = ['total']
    ordering = ['-anio', 'mes']
    list_display = ['movimiento_vehicular', 'tipo_vehiculo', 'anio', 'mes', 'valor',
                    'total', 'total_acumulado', 'variacion_interanual', 'variacion_intermensual']
    list_editable = ['tipo_vehiculo', 'valor', 'total', 'total_acumulado', 'variacion_interanual', 'variacion_intermensual']
    list_per_page = 12
    exclude = ['total_acumulado', 'variacion_interanual', 'variacion_intermensual']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
