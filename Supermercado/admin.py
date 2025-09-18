from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

# Define la función para obtener el valor total de ventas
def get_model_total_supermercado(mes, anio, valor, tipo_precio):
    return Total.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipoPrecio_id=tipo_precio
    ).values("venta_total").first()

# Define la función para calcular y guardar las variaciones
def calcular_y_guardar_variacion(obj):
    data_indicadores = {
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'tipoPrecio_id': obj.tipoPrecio_id,
        'total_venta': obj.venta_total
    }

    
    anio_anterior = int(data_indicadores['anio_id']) - 1

    # Lógica de cálculo intermensual
    if data_indicadores['mes_id'] == 1:
        mes_anterior = 12
        anio_anterior_intermensual = anio_anterior
    else:
        mes_anterior = int(data_indicadores['mes_id']) - 1
        anio_anterior_intermensual = data_indicadores['anio_id']

    data_intermensual = get_model_total_supermercado(
        mes=mes_anterior,
        anio=anio_anterior_intermensual,
        valor=data_indicadores['valor_id'],
        tipo_precio=data_indicadores['tipoPrecio_id']
    )

    # Lógica de cálculo interanual
    data_interanual = get_model_total_supermercado(
        mes=data_indicadores['mes_id'],
        anio=anio_anterior,
        valor=data_indicadores['valor_id'],
        tipo_precio=data_indicadores['tipoPrecio_id']
    )

    var_intermensual = None
    var_interanual = None

    if data_intermensual and data_intermensual['venta_total'] != 0:
        var_intermensual = (float(data_indicadores['total_venta']) / float(data_intermensual['venta_total'])) * 100 - 100

    if data_interanual and data_interanual['venta_total'] != 0:
        var_interanual = (float(data_indicadores['total_venta']) / float(data_interanual['venta_total'])) * 100 - 100

    Variacion.objects.update_or_create(
        anio=obj.anio,
        mes=obj.mes,
        valor=obj.valor,
        tipoPrecio=obj.tipoPrecio,
        defaults={
            "variacion_intermensual": round(var_intermensual, 1) if var_intermensual is not None else None,
            "variacion_interanual": round(var_interanual, 1) if var_interanual is not None else None,
        }
    )

# Usa signals para recalcular automáticamente
@receiver(post_save, sender=Total)
def total_post_save(sender, instance, created, **kwargs):
    # Recalcula la variación del objeto actual
    calcular_y_guardar_variacion(instance)

    # Recalcula la variación para el siguiente mes si existe
    next_month_obj = None
    if instance.mes.id == 12:
        next_month_obj = Total.objects.filter(
            anio_id=instance.anio.id + 1,
            mes_id=1,
            valor_id=instance.valor.id,
            tipoPrecio_id=instance.tipoPrecio.id
        ).first()
    else:
        next_month_obj = Total.objects.filter(
            anio_id=instance.anio.id,
            mes_id=instance.mes.id + 1,
            valor_id=instance.valor.id,
            tipoPrecio_id=instance.tipoPrecio.id
        ).first()

    if next_month_obj:
        calcular_y_guardar_variacion(next_month_obj)
    
    # Recalcula la variación del mismo mes del año siguiente
    next_year_obj = Total.objects.filter(
        anio_id=instance.anio.id + 1,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id,
        tipoPrecio_id=instance.tipoPrecio.id
    ).first()

    if next_year_obj:
        calcular_y_guardar_variacion(next_year_obj)


@admin.register(Total)
class SupermercadoTotalAdmin(admin.ModelAdmin):
    
    search_fields = ['anio__anio','tipoPrecio__tipo', 'valor__valor', 'venta_total']
    list_filter = ['anio__anio', 'mes__mes', 'tipoPrecio__tipo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor', 'tipoPrecio', 'venta_total']
    list_editable = ['valor', 'tipoPrecio', 'venta_total']
    list_per_page = 12

    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Variacion)
class SupermercadoVariacionAdmin(admin.ModelAdmin):
    search_fields = ['anio__anio','tipoPrecio__tipo', 'valor__valor', 'variacion_interanual', 'variacion_intermensual']
    list_filter = ['anio__anio', 'mes__mes', 'tipoPrecio__tipo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor', 'variacion_interanual', 'variacion_intermensual']
    # En esta clase, no es recomendable que los campos de variacion sean editables, ya que se calculan automáticamente
    # list_editable = ['mes', 'valor', 'variacion_interanual', 'variacion_intermensual']
    list_per_page = 12