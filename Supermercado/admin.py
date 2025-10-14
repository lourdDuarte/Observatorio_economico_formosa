from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

# ============================================================
# --- FUNCIONES AUXILIARES ---
# ============================================================

def get_model_total_supermercado(mes, anio, valor, tipo_precio):
    """Obtiene el total de ventas según los parámetros indicados."""
    return Total.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipoPrecio_id=tipo_precio
    ).values("venta_total").first()


# ============================================================
# --- CÁLCULO DE VARIACIONES ---
# ============================================================

def calcular_y_guardar_variacion(obj):
    """Calcula y guarda las variaciones intermensuales e interanuales."""
    data = {
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'tipoPrecio_id': obj.tipoPrecio_id,
        'total_venta': float(obj.venta_total)
    }

    anio_actual = data['anio_id']
    anio_anterior = anio_actual - 1

    # --- Determinar mes anterior e intermensual ---
    if data['mes_id'] == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = data['mes_id'] - 1
        anio_intermensual = anio_actual

    # --- Buscar registros previos ---
    data_intermensual = get_model_total_supermercado(
        mes=mes_anterior,
        anio=anio_intermensual,
        valor=data['valor_id'],
        tipo_precio=data['tipoPrecio_id']
    )

    data_interanual = get_model_total_supermercado(
        mes=data['mes_id'],
        anio=anio_anterior,
        valor=data['valor_id'],
        tipo_precio=data['tipoPrecio_id']
    )

    # --- Inicializar ---
    var_intermensual = 0.0
    var_interanual = 0.0

    # --- Calcular variaciones ---
    if data_intermensual and float(data_intermensual['venta_total']) != 0:
        var_intermensual = (data['total_venta'] / float(data_intermensual['venta_total'])) * 100 - 100

    if data_interanual and float(data_interanual['venta_total']) != 0:
        var_interanual = (data['total_venta'] / float(data_interanual['venta_total'])) * 100 - 100

    # --- Guardar resultados ---
    Variacion.objects.update_or_create(
        anio=obj.anio,
        mes=obj.mes,
        valor=obj.valor,
        tipoPrecio=obj.tipoPrecio,
        defaults={
            "variacion_interanual": round(var_interanual, 1),
            "variacion_intermensual": round(var_intermensual, 1)
            
        }
    )


# ============================================================
# --- SIGNALS ---
# ============================================================

@receiver(post_save, sender=Total)
def total_post_save(sender, instance, created, **kwargs):
    """Recalcula automáticamente las variaciones al guardar un registro."""
    calcular_y_guardar_variacion(instance)

    # --- Recalcular mes siguiente ---
    if instance.mes.id == 12:
        next_month = 1
        next_year = instance.anio.id + 1
    else:
        next_month = instance.mes.id + 1
        next_year = instance.anio.id

    next_obj = Total.objects.filter(
        anio_id=next_year,
        mes_id=next_month,
        valor_id=instance.valor.id,
        tipoPrecio_id=instance.tipoPrecio.id
    ).first()

    if next_obj:
        calcular_y_guardar_variacion(next_obj)

    # --- Recalcular mismo mes del año siguiente ---
    next_year_obj = Total.objects.filter(
        anio_id=instance.anio.id + 1,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id,
        tipoPrecio_id=instance.tipoPrecio.id
    ).first()

    if next_year_obj:
        calcular_y_guardar_variacion(next_year_obj)


# ============================================================
# --- ADMIN ---
# ============================================================

@admin.register(Total)
class SupermercadoTotalAdmin(admin.ModelAdmin):
    """Modelo base de datos total de ventas."""
    search_fields = ['anio__anio', 'tipoPrecio__tipo', 'valor__valor', 'venta_total']
    list_filter = ['anio__anio', 'mes__mes', 'tipoPrecio__tipo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor', 'tipoPrecio', 'venta_total']
    list_editable = ['valor', 'tipoPrecio', 'venta_total']
    list_per_page = 12

    def save_model(self, request, obj, form, change):
        """Guarda y recalcula las variaciones asociadas."""
        super().save_model(request, obj, form, change)
        calcular_y_guardar_variacion(obj)


@admin.register(Variacion)
class SupermercadoVariacionAdmin(admin.ModelAdmin):
    """Modelo de variaciones intermensuales e interanuales."""
    search_fields = ['anio__anio', 'tipoPrecio__tipo', 'valor__valor', 'variacion_interanual', 'variacion_intermensual']
    list_filter = ['anio__anio', 'mes__mes', 'tipoPrecio__tipo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['tipoPrecio','anio', 'mes', 'valor', 'variacion_interanual', 'variacion_intermensual']
    list_editable = ['anio', 'mes', 'valor', 'variacion_interanual', 'variacion_intermensual']
    list_per_page = 12
