from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
import re


# ============================================================
# --- FORM VALIDACIÓN NUMÉRICA ---
# ============================================================

class TransferenciaAdminForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = "__all__"

    def clean_total_millones(self):
        valor = self.cleaned_data.get("total_millones")

        if valor is None:
            raise ValidationError("Este campo no puede estar vacío.")

        valor_str = str(valor)

        if not re.fullmatch(r'^-?\d+(\.\d+)?$', valor_str):
            raise ValidationError(
                "Solo se permiten números con punto decimal (ej: 1500.25). No use comas ni símbolos."
            )

        return valor


# ============================================================
# --- FUNCIONES AUXILIARES ---
# ============================================================

def get_data_transferencia(anio, mes, valor):
    return Transferencia.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor
    ).first()


# ============================================================
# --- CÁLCULO VARIACIÓN INTERANUAL ---
# ============================================================

def calcular_valores(obj):

    total_millones = float(obj.total_millones)
    mes_actual = obj.mes.id
    anio_actual = obj.anio.id

    var_interanual = 0.0

    anio_anterior = anio_actual - 1

    data_interanual = get_data_transferencia(
        anio=anio_anterior,
        mes=mes_actual,
        valor=obj.valor.id,
    )

    if data_interanual and float(data_interanual.total_millones) != 0:
        var_interanual = (
            total_millones / float(data_interanual.total_millones)
        ) * 100 - 100

    return {
        'variacion_anual_nominal': str(round(var_interanual, 1)),
    }


# ============================================================
# --- SIGNAL ---
# ============================================================

@receiver(post_save, sender=Transferencia)
def indicadores_post_save_handler(sender, instance, **kwargs):

    valores_actuales = calcular_valores(instance)

    Transferencia.objects.filter(pk=instance.pk).update(
        variacion_anual_nominal=valores_actuales['variacion_anual_nominal']
    )

    # --- Recalcular mismo mes del año siguiente ---
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


# ============================================================
# --- ADMIN ---
# ============================================================

@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):

    form = TransferenciaAdminForm

    list_filter = ['anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']

    list_display = [
        'anio', 'mes', 'valor',
        'total_millones',
        'variacion_anual_nominal',
        'variacion_anual_real'
    ]

    list_editable = [
        'mes',
        'valor',
        'total_millones',
        'variacion_anual_real'
    ]

    list_per_page = 12

    exclude = ['variacion_anual_real','variacion_anual_nominal']

    def save_model(self, request, obj, form, change):

        if obj.variacion_anual_real in [None, '', 'None']:
            obj.variacion_anual_real = 0.0

        super().save_model(request, obj, form, change)

        Transferencia.objects.filter(
            pk=obj.pk,
            variacion_anual_real__isnull=True
        ).update(variacion_anual_real=0.0)