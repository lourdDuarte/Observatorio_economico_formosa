from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
# Register your models here.


def get_data_transferencia(anio,mes,valor):
    return Transferencia.objects.filter(
        mes_id = mes,
        anio_id = anio,
        valor_id = valor
    ).first()

def calcular_valores(obj):
    # Convertir a int para los cálculos
    total_millones = int(obj.total_millones) 
    mes_actual = obj.mes.id
    anio_actual = obj.anio.id

  
        

    # --- Cálculo de la Variación Interanual ---
    var_interanual = None
    anio_anterior_interanual = anio_actual - 1
    data_interanual = get_data_transferencia(
        anio=anio_anterior_interanual,
        mes=mes_actual,
        valor=obj.valor.id,
        
    )

    if data_interanual and int(data_interanual.total_millones) != 0:
        var_interanual = (total_millones / int(data_interanual.total_millones)) * 100 - 100

    return {
        'variacion_anual_nominal': str(round(var_interanual, 1)) if var_interanual is not None else None,
    }



# Signal para disparar el recálculo
@receiver(post_save, sender=Transferencia)
def indicadores_post_save_handler(sender, instance, **kwargs):
    # Obtener y actualizar los valores para el registro actual
    valores_actuales = calcular_valores(instance)
    
    Transferencia.objects.filter(pk=instance.pk).update(
        variacion_anual_nominal=valores_actuales['variacion_anual_nominal']
    )


    
    # Mismo mes del año siguiente (dependencia interanual)
    next_year_obj = get_data_transferencia(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        valor=instance.valor.id,
       
    )

    if next_year_obj:
        valores_siguiente_anio = calcular_valores(next_year_obj)
        Transferencia.objects.filter(pk=next_year_obj.pk).update(
            variacion_anual_nominal=valores_siguiente_anio['variacion_anual_nominal']
        )

## Configuración del Admin
@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor',  'total_millones', 'variacion_anual_nominal', 'variacion_anual_real']
    list_editable = ['mes', 'valor',  'total_millones', 'variacion_anual_nominal', 'variacion_anual_real'] 
    list_per_page = 12
    exclude = ['variacion_anual_nominal', 'variacion_anual_real']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)