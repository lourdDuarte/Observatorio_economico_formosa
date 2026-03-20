from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

admin.site.register(TipoCultivo)
# Register your models here.
# ============================================================
# --- FUNCIONES AUXILIARES ---
# ============================================================

def get_model_indicadores_precio(mes, anio, tipo_cultivo):
    """Obtiene el total de ventas según los parámetros indicados."""
    return IndicadoresPrecioCultivo.objects.filter(
        mes_id=mes,
        anio_id=anio,
        tipo_cultivo_id=tipo_cultivo
    ).first()



# ============================================================
# --- CÁLCULO DE VARIACIONES ---
# ============================================================

def calcular_valores(obj):
    # mes anterior...
    if obj.mes.id == 1:
        mes_anterior = 12
        anio_intermensual = obj.anio.id - 1
    else:
        mes_anterior = obj.mes.id - 1
        anio_intermensual = obj.anio.id

    data_intermensual = get_model_indicadores_precio(
        mes=mes_anterior,
        anio=anio_intermensual,
        tipo_cultivo=obj.tipo_cultivo.id
    )

    var_mensual = 0.0
    var_fob = 0.0

    # ✅ convertir obj también
    pn_actual = float(obj.precio_nacional)
    pi_actual = float(obj.precio_internacional)

    if data_intermensual:
        pn_anterior = float(data_intermensual.precio_nacional)
        pi_anterior = float(data_intermensual.precio_internacional)

        if pn_anterior != 0:
            var_mensual = (pn_actual / pn_anterior) * 100 - 100
        if pi_anterior != 0:
            var_fob = (pi_actual / pi_anterior) * 100 - 100

    return {
        'variacion_mensual': str(round(var_mensual, 1)),
        'variacion_fob': str(round(var_fob, 1)),
    }



# --- Signal ---
@receiver(post_save, sender=IndicadoresPrecioCultivo)
def indicadores_post_save_handler(sender, instance, **kwargs):
    valores_actuales = calcular_valores(instance)
    IndicadoresPrecioCultivo.objects.filter(pk=instance.pk).update(
        variacion_mensual=valores_actuales['variacion_mensual'],
        variacion_fob=valores_actuales['variacion_fob']
    )

    # --- Recalcular todos los posteriores del mismo año ---
    posteriores = IndicadoresPrecioCultivo.objects.filter(
        anio=instance.anio,
        tipo_cultivo=instance.tipo_cultivo.id,
        mes__id__gt=instance.mes.id
    ).order_by('mes__id')

    
    for indicador in posteriores:
        
        valores = calcular_valores(indicador)
        IndicadoresPrecioCultivo.objects.filter(pk=indicador.pk).update(
            
            variacion_mensual=valores['variacion_mensual'],
            variacion_fob=valores['variacion_fob']
        )

    # --- También recalcular el mismo mes del año siguiente ---
    siguiente_anio = get_model_indicadores_precio(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        tipo_cultivo=instance.tipo_cultivo.id,
    
    )
    if siguiente_anio:
        valores_siguiente_anio = calcular_valores(siguiente_anio)
        IndicadoresPrecioCultivo.objects.filter(pk=siguiente_anio.pk).update(
            
            variacion_mensual=valores_siguiente_anio['variacion_mensual'],
            variacion_fob=valores_siguiente_anio['variacion_fob']
        )


# --- Admin ---
@admin.register(IndicadoresPrecioCultivo)
class IndicadoresPrecioCultivoAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'tipo_cultivo__tipo_cultivo']
    ordering = ['-anio', 'mes']
    list_display = ['tipo_cultivo', 'anio', 'mes', 'precio_nacional',
                    'precio_internacional', 'variacion_mensual', 'variacion_fob']
    list_editable = [ 'precio_nacional',
                    'precio_internacional', 'variacion_mensual', 'variacion_fob']
    list_per_page = 12
    exclude = ['variacion_mensual', 'variacion_fob']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)




from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProduccionCampaniaCultivo, ParticipacionProdFormosa


def get_produccion(tipo_cultivo, campania, valor_nombre):
    return ProduccionCampaniaCultivo.objects.filter(
        tipo_cultivo=tipo_cultivo,
        campania=campania,
        valor__valor=valor_nombre  # 👈 asume que Valor tiene campo "valor"
    ).first()


def calcular_participacion(instance):
    tipo_cultivo = instance.tipo_cultivo
    campania = instance.campania

    # Buscar ambas producciones
    formosa = get_produccion(tipo_cultivo, campania, "Formosa")
    nacional = get_produccion(tipo_cultivo, campania, "Nacional")

    # ❌ Si falta uno → no calcular
    if not formosa or not nacional:
        return

    try:
        prod_formosa = float(formosa.produccion)
        prod_nacional = float(nacional.produccion)

        if prod_nacional == 0:
            participacion = 0
        else:
            participacion = (prod_formosa / prod_nacional) * 100

    except Exception:
        return

    # ✅ Guardar o actualizar
    ParticipacionProdFormosa.objects.update_or_create(
        tipo_cultivo=tipo_cultivo,
        campania=campania,
        defaults={
            "participacion": round(participacion, 2)
        }
    )


@receiver(post_save, sender=ProduccionCampaniaCultivo)
def actualizar_participacion(sender, instance, **kwargs):
    """
    Se ejecuta cada vez que se guarda ProduccionCampaniaCultivo
    """
    calcular_participacion(instance)

    # 🔥 CLAVE: recalcular también el "par" por si se modificó uno existente
    otro_valor = "Nacional" if instance.valor.valor == "Formosa" else "Formosa"

    otro = ProduccionCampaniaCultivo.objects.filter(
        tipo_cultivo=instance.tipo_cultivo,
        campania=instance.campania,
        valor__valor=otro_valor
    ).first()

    if otro:
        calcular_participacion(otro)

from django.contrib import admin
from .models import ProduccionCampaniaCultivo, ParticipacionProdFormosa


# ============================================================
# PRODUCCION (manual)
# ============================================================

@admin.register(ProduccionCampaniaCultivo)
class ProduccionCampaniaCultivoAdmin(admin.ModelAdmin):

    list_display = [
        'tipo_cultivo',
        'campania',
        'valor',
        'superficie_sembrada',
        'superficie_cosechada',
        'produccion',
        'fecha_actualizacion'
    ]

    list_filter = [
        'tipo_cultivo',
        'campania',
        'valor'
    ]

    ordering = ['-campania', 'tipo_cultivo']

    search_fields = [
        'tipo_cultivo__tipo_cultivo',
        'campania__campania',
        'valor__valor'
    ]

    list_per_page = 20


# ============================================================
# PARTICIPACION (automática)
# ============================================================

@admin.register(ParticipacionProdFormosa)
class ParticipacionProdFormosaAdmin(admin.ModelAdmin):

    list_display = [
        'tipo_cultivo',
        'campania',
        'participacion'
    ]

    list_filter = [
        'tipo_cultivo',
        'campania'
    ]

    ordering = ['-campania', 'tipo_cultivo']

    search_fields = [
        'tipo_cultivo__tipo_cultivo',
        'campania__campania'
    ]

    list_per_page = 20

   