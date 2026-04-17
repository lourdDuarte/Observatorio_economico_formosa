from django.contrib import admin
from .models import *
from django import forms
from django.core.exceptions import ValidationError
from django.dispatch import receiver
import re
from django.db.models.signals import post_save
# Register your models here.
admin.site.register(TipoAcceso)


class AccesoInternetAdminForm(forms.ModelForm):
    class Meta:
        model = AccesoInternet
        fields = "__all__"

    def clean_total(self):
        valor = self.cleaned_data.get("cantidad")

        if valor is None:
            raise ValidationError("Este campo no puede estar vacío.")

        valor_str = str(valor)

        if not re.fullmatch(r'^\d+(\.\d+)?$', valor_str):
            raise ValidationError(
                "Solo se permiten números con punto decimal (ej: 4526.12). No use comas ni símbolos."
            )

        return valor


# =====================================================
# FUNCIÓN AUXILIAR
# =====================================================
def get_data_acceso_internet(mes, anio, valor, tipo_acceso):
    return AccesoInternet.objects.filter(
        mes_id = mes,
        anio_id = anio,
        valor_id = valor,
        tipo_acceso_id = tipo_acceso).first()


def calcular_valores(obj):

    cantidad_actual = float(obj.cantidad)
    mes_actual = obj.mes.id
    anio_actual = obj.anio.id



    # -------------------
    # INTERANUAL
    # -------------------
    var_interanual = 0.0

    data_interanual = get_data_acceso_internet(
        mes=mes_actual,
        anio=anio_actual - 1,
        valor=obj.valor.id,
        tipo_acceso=obj.tipo_acceso.id
    )

    if data_interanual and float(data_interanual.cantidad) != 0:
        var_interanual = (
            cantidad_actual / float(data_interanual.cantidad)
        ) * 100 - 100

    return {
        'variacion_interanual': str(round(var_interanual, 1)),
    }

# =====================================================
# SIGNAL
# =====================================================

@receiver(post_save, sender=AccesoInternet)
def indicadores_post_save_handler(sender, instance, **kwargs):

    valores_actuales = calcular_valores(instance)

    AccesoInternet.objects.filter(pk=instance.pk).update(
        variacion_interanual=valores_actuales['variacion_interanual']
    )

    posteriores = AccesoInternet.objects.filter(
        anio=instance.anio,
        valor=instance.valor,
        tipo_acceso=instance.tipo_acceso,
        mes__id__gt=instance.mes.id
    ).order_by('mes__id')

   

    for indicador in posteriores:

    

        valores = calcular_valores(indicador)
        

        AccesoInternet.objects.filter(pk=indicador.pk).update(
            variacion_interanual=valores['variacion_interanual']
        )

    siguiente_anio = get_data_acceso_internet(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        valor=instance.valor.id,
        tipo_acceso=instance.tipo_acceso.id
    )

    if siguiente_anio:
        valores_siguiente_anio = calcular_valores(siguiente_anio)

        AccesoInternet.objects.filter(pk=siguiente_anio.pk).update(
            variacion_interanual=valores_siguiente_anio['variacion_interanual']
        )



# =====================================================
# ADMIN
# =====================================================

@admin.register(AccesoInternet)
class AccesoInternetAdmin(admin.ModelAdmin):

    form = AccesoInternetAdminForm

    list_filter = ['anio__anio', 'mes__mes', 
                   'tipo_acceso__tipo', 'valor__valor']

    search_fields = ['cantidad']

    ordering = ['-anio', 'mes']

    list_display = [ 'tipo_acceso', 'anio', 'mes',
                    'valor', 'cantidad', 
                    'variacion_interanual']

    list_editable = [ 'valor', 'cantidad',  'variacion_interanual']

    list_per_page = 12

    exclude = [
               'variacion_interanual']

