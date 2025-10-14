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
            recaudacion_acumulada += float(recaudacion_anterior.recaudacion_acumulada)

    # --- Variación intermensual ---
    var_intermensual = 0.0
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
    var_interanual = 0.0
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
        'variacion_intermensual': str(round(var_intermensual, 1)),
        'variacion_interanual': str(round(var_interanual, 1)),
    }

# --- Signal para recalcular al guardar un registro de Recaudacion
@receiver(post_save, sender=Recaudacion)
def recaudacion_post_save_handler(sender, instance, **kwargs):
    # Calcular valores del registro actual
    valores_actuales = calcular_valores(instance)
    Recaudacion.objects.filter(pk=instance.pk).update(
        recaudacion_acumulada=valores_actuales['recaudacion_acumulada']
    )

    # Actualizar o crear indicador correspondiente
    indicador, created = Indicadores.objects.get_or_create(
        anio=instance.anio,
        mes=instance.mes,
        valor=instance.valor,
        tipo=instance.tipo,
        defaults={
            'variacion_intermensual': valores_actuales['variacion_intermensual'],
            'variacion_interanual': valores_actuales['variacion_interanual'],
        }
    )
    if not created:
        Indicadores.objects.filter(pk=indicador.pk).update(
            variacion_intermensual=valores_actuales['variacion_intermensual'],
            variacion_interanual=valores_actuales['variacion_interanual']
        )

    # --- Recalcular todos los meses posteriores del mismo año ---
    posteriores = Recaudacion.objects.filter(
        anio=instance.anio,
        valor=instance.valor,
        tipo=instance.tipo,
        mes__id__gt=instance.mes.id
    ).order_by('mes__id')

    acumulado = float(valores_actuales['recaudacion_acumulada'])
    for rec in posteriores:
        acumulado += float(rec.recaudacion)
        valores = calcular_valores(rec)
        valores['recaudacion_acumulada'] = str(acumulado)
        Recaudacion.objects.filter(pk=rec.pk).update(
            recaudacion_acumulada=valores['recaudacion_acumulada']
        )
        # Sincronizar con Indicadores
        indicador_posterior, _ = Indicadores.objects.get_or_create(
            anio=rec.anio,
            mes=rec.mes,
            valor=rec.valor,
            tipo=rec.tipo
        )
        Indicadores.objects.filter(pk=indicador_posterior.pk).update(
            variacion_intermensual=valores['variacion_intermensual'],
            variacion_interanual=valores['variacion_interanual']
        )

    # --- Recalcular mismo mes del año siguiente ---
    siguiente_anio = get_recaudacion(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        valor=instance.valor.id,
        tipo=instance.tipo.id
    )
    if siguiente_anio:
        valores_siguiente_anio = calcular_valores(siguiente_anio)
        Recaudacion.objects.filter(pk=siguiente_anio.pk).update(
            recaudacion_acumulada=valores_siguiente_anio['recaudacion_acumulada']
        )
        indicador_next, _ = Indicadores.objects.get_or_create(
            anio=siguiente_anio.anio,
            mes=siguiente_anio.mes,
            valor=siguiente_anio.valor,
            tipo=siguiente_anio.tipo
        )
        Indicadores.objects.filter(pk=indicador_next.pk).update(
            variacion_intermensual=valores_siguiente_anio['variacion_intermensual'],
            variacion_interanual=valores_siguiente_anio['variacion_interanual']
        )

# --- Configuración del Admin ---
@admin.register(Recaudacion)
class RecaudacionAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo__tipo']
    search_fields = ['recaudacion']
    ordering = ['-anio', 'mes']
    list_display = ['tipo','anio', 'mes', 'valor',  'recaudacion', 'recaudacion_acumulada']
    list_editable = ['anio','mes', 'valor', 'recaudacion', 'recaudacion_acumulada']
    list_per_page = 12
    exclude = ['recaudacion_acumulada']

@admin.register(Indicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo__tipo']
    ordering = ['-anio', 'mes']
    list_display = ['tipo', 'anio', 'mes', 'valor',  'variacion_intermensual', 'variacion_interanual']
    list_editable = ['anio', 'mes', 'valor', 'variacion_intermensual', 'variacion_interanual']
    list_per_page = 12
