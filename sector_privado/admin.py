from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver


@admin.register(IndicadoresPrivado)
class IndicadoresPrivadoAdmin(admin.ModelAdmin):
    list_filter = ['tipo__tipo','anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['tipo','anio', 'mes', 'valor',  'variacion_interanual', 'variacion_intermensual', 'diferencia_intermensual', 'diferencia_interanual']
    list_editable = [ 'mes', 'valor',  'variacion_interanual', 'variacion_intermensual', 'diferencia_intermensual', 'diferencia_interanual'] 
    list_per_page = 12

def get_model_cantidades_privado(mes,anio,valor,tipo, estacionalidad):
    return CantidadesPrivado.objects.filter(
        mes_id = mes,
        anio_id = anio,
        valor_id = valor,
        tipo = tipo,
        estacionalidad = estacionalidad
    ).values("cantidad").first()


def calcular_y_guardar_variacion(obj):
    # Preparamos los datos del objeto
    data_indicadores = {
        'tipo': obj.tipo,
        'estacionalidad_id': obj.estacionalidad.id,
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'cantidad': obj.cantidad
    }

    anio_anterior = int(data_indicadores['anio_id']) - 1

    # Determinar mes y año para intermensual
    if data_indicadores['mes_id'] == 1:
        mes_anterior = 12
        anio_anterior_intermensual = anio_anterior
    else:
        mes_anterior = int(data_indicadores['mes_id']) - 1
        anio_anterior_intermensual = data_indicadores['anio_id']

    # Obtener datos previos
    data_intermensual = get_model_cantidades_privado(
        mes=mes_anterior,
        anio=anio_anterior_intermensual,
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

    # Inicializamos variables
    var_intermensual = None
    var_interanual = None
    dif_intermensual = None
    dif_interanual = None

    # Calcular intermensual si hay datos
    if data_intermensual and data_intermensual['cantidad'] != 0:
        var_intermensual = (float(data_indicadores['cantidad']) / float(data_intermensual['cantidad'])) * 100 - 100
        dif_intermensual = float(data_indicadores['cantidad']) - float(data_intermensual['cantidad'])

    # Calcular interanual si hay datos
    if data_interanual and data_interanual['cantidad'] != 0:
        var_interanual = (float(data_indicadores['cantidad']) / float(data_interanual['cantidad'])) * 100 - 100
        dif_interanual = float(data_indicadores['cantidad']) - float(data_interanual['cantidad'])

    # Guardar en la base de datos, asegurando valores válidos
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


# Usa signals para recalcular automáticamente
@receiver(post_save, sender=CantidadesPrivado)
def total_post_save(sender, instance, created, **kwargs):
    # Recalcula la variación del objeto actual
    calcular_y_guardar_variacion(instance)

    # Recalcula la variación para el siguiente mes si existe
    next_month_obj = None
    if instance.mes.id == 12:
        next_month_obj = CantidadesPrivado.objects.filter(
            tipo = instance.tipo,
            anio_id=instance.anio.id + 1,
            estacionalidad = instance.estacionalidad.id,
            mes_id=1,
            valor_id=instance.valor.id
        ).first()
    else:
        next_month_obj = CantidadesPrivado.objects.filter(
            tipo = instance.tipo,
            anio_id=instance.anio.id,
            estacionalidad = instance.estacionalidad.id,
            mes_id=instance.mes.id + 1,
            valor_id=instance.valor.id,
           
        ).first()

    if next_month_obj:
        calcular_y_guardar_variacion(next_month_obj)
    
    # Recalcula la variación del mismo mes del año siguiente
    next_year_obj = CantidadesPrivado.objects.filter(
        tipo = instance.tipo,
        anio_id=instance.anio.id + 1,
        estacionalidad = instance.estacionalidad.id,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id,
     
    ).first()

    if next_year_obj:
        calcular_y_guardar_variacion(next_year_obj)

@admin.register(CantidadesPrivado)
class CantidadesPrivadoAdmin(admin.ModelAdmin):


    list_filter = ['tipo__tipo','anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['tipo','estacionalidad','anio', 'mes', 'valor',  'cantidad']
    list_editable = ['estacionalidad','anio', 'mes', 'valor',  'cantidad'] 
    list_per_page = 12

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

