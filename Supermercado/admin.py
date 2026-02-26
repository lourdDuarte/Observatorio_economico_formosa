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

class SupermercadoTotalAdminForm(forms.ModelForm):
    class Meta:
        model = Total
        fields = "__all__"

    def clean_venta_total(self):
        valor = self.cleaned_data.get("venta_total")

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

def get_model_total_supermercado(mes, anio, valor, tipo_precio):
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

    data = {
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'tipoPrecio_id': obj.tipoPrecio_id,
        'total_venta': float(obj.venta_total)
    }

    anio_actual = data['anio_id']
    anio_anterior = anio_actual - 1

    if data['mes_id'] == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = data['mes_id'] - 1
        anio_intermensual = anio_actual

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

    var_intermensual = 0.0
    var_interanual = 0.0

    if data_intermensual and float(data_intermensual['venta_total']) != 0:
        prev = float(data_intermensual['venta_total'])
        var_intermensual = (data['total_venta'] / prev) * 100 - 100

    if data_interanual and float(data_interanual['venta_total']) != 0:
        prev = float(data_interanual['venta_total'])
        var_interanual = (data['total_venta'] / prev) * 100 - 100

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

    calcular_y_guardar_variacion(instance)

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

    form = SupermercadoTotalAdminForm

    search_fields = ['anio__anio', 'tipoPrecio__tipo',
                     'valor__valor', 'venta_total']
    list_filter = ['anio__anio', 'mes__mes',
                   'tipoPrecio__tipo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor',
                    'tipoPrecio', 'venta_total']
    list_editable = ['valor', 'tipoPrecio', 'venta_total']
    list_per_page = 12


@admin.register(Variacion)
class SupermercadoVariacionAdmin(admin.ModelAdmin):

    search_fields = ['anio__anio', 'tipoPrecio__tipo',
                     'valor__valor',
                     'variacion_interanual',
                     'variacion_intermensual']

    list_filter = ['anio__anio', 'mes__mes',
                   'tipoPrecio__tipo', 'valor__valor']

    ordering = ['-anio', 'mes']

    list_display = ['tipoPrecio', 'anio', 'mes',
                    'valor',
                    'variacion_interanual',
                    'variacion_intermensual']

    list_editable = ['anio', 'mes', 'valor',
                     'variacion_interanual',
                     'variacion_intermensual']

    list_per_page = 12