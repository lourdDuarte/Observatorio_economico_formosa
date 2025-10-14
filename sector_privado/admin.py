# admin.py (refactor para evitar recursion infinita)
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *


# ============================================================
# --- FUNCIONES AUXILIARES ---
# ============================================================

def get_model_cantidades_privado(mes, anio, valor, tipo, estacionalidad):
    """Obtiene la cantidad para los parámetros indicados."""
    return CantidadesPrivado.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipo=tipo,
        estacionalidad=estacionalidad
    ).values("cantidad").first()


# ============================================================
# --- CÁLCULO VARIACIONES: CantidadesPrivado ---
# ============================================================


def calcular_y_guardar_variacion(obj):
    """Calcula y guarda las variaciones intermensuales e interanuales del modelo CantidadesPrivado."""
    data_indicadores = {
        'tipo': obj.tipo,
        'estacionalidad_id': obj.estacionalidad.id,
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'cantidad': obj.cantidad
    }

    anio_actual = data_indicadores['anio_id']
    anio_anterior = anio_actual - 1

    # --- Definir mes/año intermensual ---
    if data_indicadores['mes_id'] == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = data_indicadores['mes_id'] - 1
        anio_intermensual = anio_actual

    # --- Buscar datos previos ---
    data_intermensual = get_model_cantidades_privado(
        mes=mes_anterior,
        anio=anio_intermensual,
        valor=data_indicadores['valor_id'],
        tipo=data_indicadores['tipo'],
        estacionalidad=data_indicadores['estacionalidad_id']
    )

    data_interanual = get_model_cantidades_privado(
        mes=data_indicadores['mes_id'],
        anio=anio_anterior,
        valor=data_indicadores['valor_id'],
        tipo=data_indicadores['tipo'],
        estacionalidad=data_indicadores['estacionalidad_id']
    )

    # --- Inicialización ---
    var_intermensual = var_interanual = None
    dif_intermensual = dif_interanual = None

    # --- Calcular variaciones ---
    if data_intermensual and data_intermensual['cantidad'] != 0:
        cantidad_actual = float(data_indicadores['cantidad'])
        cantidad_prev = float(data_intermensual['cantidad'])
        var_intermensual = (cantidad_actual / cantidad_prev) * 100 - 100
        dif_intermensual = cantidad_actual - cantidad_prev

    if data_interanual and data_interanual['cantidad'] != 0:
        cantidad_actual = float(data_indicadores['cantidad'])
        cantidad_prev = float(data_interanual['cantidad'])
        var_interanual = (cantidad_actual / cantidad_prev) * 100 - 100
        dif_interanual = cantidad_actual - cantidad_prev

    # --- Guardar resultado en IndicadoresPrivado tal como estaba ---
    IndicadoresPrivado.objects.update_or_create(
        tipo=obj.tipo,
        estacionalidad=obj.estacionalidad,
        anio=obj.anio,
        mes=obj.mes,
        valor=obj.valor,
        defaults={
            "variacion_interanual": round(var_interanual, 1) if var_interanual is not None else 0.0,
            "variacion_intermensual": round(var_intermensual, 1) if var_intermensual is not None else 0.0,
            "diferencia_interanual": round(dif_interanual, 1) if dif_interanual is not None else 0.0,
            "diferencia_intermensual": round(dif_intermensual, 1) if dif_intermensual is not None else 0.0,
        }
    )

@receiver(post_save, sender=CantidadesPrivado)
def total_post_save(sender, instance, created, **kwargs):
    """Recalcula automáticamente variaciones al guardar un registro."""
    # recalcula el indicador del objeto actual
    calcular_y_guardar_variacion(instance)

    # --- Recalcular siguiente mes ---
    if instance.mes.id == 12:
        next_obj = CantidadesPrivado.objects.filter(
            tipo=instance.tipo,
            anio_id=instance.anio.id + 1,
            estacionalidad=instance.estacionalidad.id,
            mes_id=1,
            valor_id=instance.valor.id
        ).first()
    else:
        next_obj = CantidadesPrivado.objects.filter(
            tipo=instance.tipo,
            anio_id=instance.anio.id,
            estacionalidad=instance.estacionalidad.id,
            mes_id=instance.mes.id + 1,
            valor_id=instance.valor.id
        ).first()

    if next_obj:
        # llamar a la misma función: no hace save() sobre CantidadesPrivado, sólo actualiza IndicadoresPrivado
        calcular_y_guardar_variacion(next_obj)

    # --- Recalcular mismo mes del año siguiente ---
    next_year_obj = CantidadesPrivado.objects.filter(
        tipo=instance.tipo,
        anio_id=instance.anio.id + 1,
        estacionalidad=instance.estacionalidad.id,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id
    ).first()

    if next_year_obj:
        calcular_y_guardar_variacion(next_year_obj)

# ============================================================
# --- CÁLCULO VARIACIONES: RemuneracionRama ---
# ============================================================

def get_remuneracion_rama(mes, anio, valor, rama, estacionalidad):
    """Obtiene la remuneración para los parámetros indicados."""
    return RemuneracionRama.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        rama_id=rama,
        estacionalidad_id=estacionalidad
    ).values("remuneracion").first()


def calcular_y_guardar_variacion_remuneracion(obj):
    """
    Calcula variaciones para RemuneracionRama.
    IMPORTANTE: NO usar obj.save() aquí para evitar disparar post_save recursivamente.
    Usamos .update(...) sobre el queryset para escribir las variaciones sin señales.
    """
    data = {
        'rama_id': obj.rama.id,
        'estacionalidad_id': obj.estacionalidad.id,
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'remuneracion': int(obj.remuneracion)
    }

    anio_actual = data['anio_id']
    anio_anterior = anio_actual - 1

    # --- Definir mes/año intermensual ---
    if data['mes_id'] == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = data['mes_id'] - 1
        anio_intermensual = anio_actual

    # --- Buscar datos previos ---
    data_intermensual = get_remuneracion_rama(
        mes=mes_anterior,
        anio=anio_intermensual,
        valor=data['valor_id'],
        rama=data['rama_id'],
        estacionalidad=data['estacionalidad_id']
    )

    data_interanual = get_remuneracion_rama(
        mes=data['mes_id'],
        anio=anio_anterior,
        valor=data['valor_id'],
        rama=data['rama_id'],
        estacionalidad=data['estacionalidad_id']
    )

    # --- Cálculos ---
    var_intermensual = 0.0
    var_interanual = 0.0

    if data_intermensual and int(data_intermensual['remuneracion']) != 0:
        var_intermensual = (data['remuneracion'] / int(data_intermensual['remuneracion'])) * 100 - 100

    if data_interanual and int(data_interanual['remuneracion']) != 0:
        var_interanual = (data['remuneracion'] / int(data_interanual['remuneracion'])) * 100 - 100

    # --- Actualizar el registro directamente evitando obj.save() (evitar señales) ---
    RemuneracionRama.objects.filter(pk=obj.pk).update(
        variacion_intermensual=round(var_intermensual, 1),
        variacion_interanual=round(var_interanual, 1)
    )


@receiver(post_save, sender=RemuneracionRama)
def recalcular_variacion_remuneracion(sender, instance, created, **kwargs):
    """Recalcula automáticamente variaciones al guardar un registro."""
    # recalcula el registro actual (esto no disparará post_save porque usamos update en la función)
    calcular_y_guardar_variacion_remuneracion(instance)

    # --- Recalcular mes siguiente ---
    if instance.mes.id == 12:
        next_month = 1
        next_year = instance.anio.id + 1
    else:
        next_month = instance.mes.id + 1
        next_year = instance.anio.id

    next_obj = RemuneracionRama.objects.filter(
        rama=instance.rama,
        estacionalidad=instance.estacionalidad,
        anio_id=next_year,
        mes_id=next_month,
        valor=instance.valor
    ).first()

    if next_obj:
        # recalcula siguiente mes sin disparar señales
        calcular_y_guardar_variacion_remuneracion(next_obj)

    # --- Recalcular mismo mes del año siguiente ---
    next_year_obj = RemuneracionRama.objects.filter(
        rama=instance.rama,
        estacionalidad=instance.estacionalidad,
        anio_id=instance.anio.id + 1,
        mes_id=instance.mes.id,
        valor=instance.valor
    ).first()

    if next_year_obj:
        calcular_y_guardar_variacion_remuneracion(next_year_obj)




# ============================================================
# --- ADMIN ---
# ============================================================


@admin.register(CantidadesPrivado)
class CantidadesPrivadoAdmin(admin.ModelAdmin):
    list_filter = ['tipo__tipo', 'anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['tipo', 'estacionalidad', 'anio', 'mes', 'valor', 'cantidad']
    list_editable = ['estacionalidad', 'anio', 'mes', 'valor', 'cantidad']
    list_per_page = 12
 

@admin.register(AsalariadoRama)
class AsalariadoRamaPrivadoAdmin(admin.ModelAdmin): 
    list_filter = ['rama__rama', 'trimestre__trimestre', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['rama', 'trimestre', 'anio', 'mes', 'valor', 'cantidad']
    list_editable = ['trimestre', 'anio', 'mes', 'valor', 'cantidad']
    list_per_page = 12


@admin.register(IndicadoresPrivado)
class IndicadoresPrivadoAdmin(admin.ModelAdmin):
    list_filter = ['tipo__tipo', 'anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = [
        'tipo', 'anio', 'mes', 'valor',
        'variacion_interanual', 'variacion_intermensual',
        'diferencia_intermensual', 'diferencia_interanual'
    ]
    list_editable = [
        'mes', 'valor',
        'variacion_interanual', 'variacion_intermensual',
        'diferencia_intermensual', 'diferencia_interanual'
    ]
    list_per_page = 12

@admin.register(RemuneracionRama)
class RemuneracionRamaAdmin(admin.ModelAdmin):
   
    list_filter = ['rama__rama', 'anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['rama', 'anio', 'mes', 'valor', 'remuneracion',
                    'variacion_interanual', 'variacion_intermensual']
    list_editable = ['anio', 'mes', 'valor', 'remuneracion',
                     'variacion_interanual', 'variacion_intermensual']
    exclude = ['variacion_interanual', 'variacion_intermensual']
    list_per_page = 12
