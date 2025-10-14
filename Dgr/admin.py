from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Función auxiliar para buscar registros de Recaudacion
def get_recaudacion(mes, anio, valor, tipo):
    return Recaudacion.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipo_id=tipo
    ).first()

# --- Función auxiliar para buscar registros de Indicadores
def get_indicador(mes, anio, valor, tipo):
    return Indicadores.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipo_id=tipo
    ).first()

# --- Función central para calcular recaudacion acumulada + variaciones
def calcular_valores(obj):
    recaudacion_actual = int(obj.recaudacion)
    mes_actual = obj.mes.id
    anio_actual = obj.anio.id

    # --- Cálculo recaudación acumulada ---
    recaudacion_acumulada = recaudacion_actual
    if mes_actual > 1:
        recaudacion_anterior = get_recaudacion(
            mes=mes_actual - 1,
            anio=anio_actual,
            valor=obj.valor.id,
            tipo=obj.tipo.id
        )
        if recaudacion_anterior and recaudacion_anterior.recaudacion_acumulada:
            recaudacion_acumulada = recaudacion_actual + float(recaudacion_anterior.recaudacion_acumulada)

    # --- Variación intermensual ---
    var_intermensual = None
    if mes_actual == 1:
        mes_anterior = 12
        anio_anterior = anio_actual - 1
    else:
        mes_anterior = mes_actual - 1
        anio_anterior = anio_actual

    data_intermensual = get_recaudacion(
        mes=mes_anterior,
        anio=anio_anterior,
        valor=obj.valor.id,
        tipo=obj.tipo.id
    )
    if data_intermensual and int(data_intermensual.recaudacion) != 0:
        var_intermensual = (recaudacion_actual / int(data_intermensual.recaudacion)) * 100 - 100

    # --- Variación interanual ---
    var_interanual = None
    data_interanual = get_recaudacion(
        mes=mes_actual,
        anio=anio_actual - 1,
        valor=obj.valor.id,
        tipo=obj.tipo.id
    )
    if data_interanual and int(data_interanual.recaudacion) != 0:
        var_interanual = (recaudacion_actual / int(data_interanual.recaudacion)) * 100 - 100

    return {
        'recaudacion_acumulada': str(recaudacion_acumulada),
        'variacion_intermensual': str(round(var_intermensual, 1)) if var_intermensual is not None else None,
        'variacion_interanual': str(round(var_interanual, 1)) if var_interanual is not None else None,
    }

# --- Signal para recalcular cuando se guarda un registro de Recaudacion
@receiver(post_save, sender=Recaudacion)
def recaudacion_post_save_handler(sender, instance, **kwargs):
    valores = calcular_valores(instance)

    # Actualizar el propio registro con recaudación acumulada
    Recaudacion.objects.filter(pk=instance.pk).update(
        recaudacion_acumulada=valores['recaudacion_acumulada']
    )

    # Crear/Actualizar registro en Indicadores
    indicador, created = Indicadores.objects.get_or_create(
        anio=instance.anio,
        mes=instance.mes,
        valor=instance.valor,
        tipo=instance.tipo,
        defaults={
            'variacion_intermensual': valores['variacion_intermensual'],
            'variacion_interanual': valores['variacion_interanual'],
        }
    )
    if not created:
        Indicadores.objects.filter(pk=indicador.pk).update(
            variacion_intermensual=valores['variacion_intermensual'],
            variacion_interanual=valores['variacion_interanual']
        )

    # --- Propagar cambios hacia adelante ---
    # Recalcular siguiente mes
    if instance.mes.id < 12:
        siguiente_mes = get_recaudacion(
            mes=instance.mes.id + 1,
            anio=instance.anio.id,
            valor=instance.valor.id,
            tipo=instance.tipo.id
        )
    else:
        siguiente_mes = get_recaudacion(
            mes=1,
            anio=instance.anio.id + 1,
            valor=instance.valor.id,
            tipo=instance.tipo.id
        )
    if siguiente_mes:
        recaudacion_post_save_handler(Recaudacion, siguiente_mes)

    # Recalcular mismo mes del año siguiente
    siguiente_anio = get_recaudacion(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        valor=instance.valor.id,
        tipo=instance.tipo.id
    )
    if siguiente_anio:
        recaudacion_post_save_handler(Recaudacion, siguiente_anio)


# --- Configuración del Admin
@admin.register(Recaudacion)
class RecaudacionAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo__tipo']
    search_fields = ['recaudacion']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor', 'tipo', 'recaudacion', 'recaudacion_acumulada']
    list_editable = ['mes', 'valor', 'tipo', 'recaudacion', 'recaudacion_acumulada']
    list_per_page = 12
    exclude = ['recaudacion_acumulada']

@admin.register(Indicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo__tipo']
    search_fields = []
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor', 'tipo', 'variacion_intermensual', 'variacion_interanual']
    list_editable = []
    list_per_page = 12
    exclude = []
