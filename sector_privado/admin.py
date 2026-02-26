from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
import re


# ============================================================
# --- VALIDACIÓN NUMÉRICA ---
# ============================================================

class CantidadesPrivadoAdminForm(forms.ModelForm):
    class Meta:
        model = CantidadesPrivado
        fields = "__all__"

    def clean_cantidad(self):
        valor = self.cleaned_data.get("cantidad")

        if valor is None:
            raise ValidationError("Este campo no puede estar vacío.")

        valor_str = str(valor)

        if not re.fullmatch(r'^-?\d+(\.\d+)?$', valor_str):
            raise ValidationError(
                "Solo se permiten números con punto decimal (ej: 1500.25). No use comas ni símbolos."
            )

        return valor


class RemuneracionRamaAdminForm(forms.ModelForm):
    class Meta:
        model = RemuneracionRama
        fields = "__all__"

    def clean_remuneracion(self):
        valor = self.cleaned_data.get("remuneracion")

        if valor is None:
            raise ValidationError("Este campo no puede estar vacío.")

        valor_str = str(valor)

        if not re.fullmatch(r'^-?\d+(\.\d+)?$', valor_str):
            raise ValidationError(
                "Solo se permiten números con punto decimal (ej: 250000.50). No use comas ni símbolos."
            )

        return valor


# ============================================================
# --- FUNCIONES AUXILIARES ---
# ============================================================

def get_model_cantidades_privado(mes, anio, valor, tipo, estacionalidad):
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

    data = {
        'tipo': obj.tipo,
        'estacionalidad_id': obj.estacionalidad.id,
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'cantidad': float(obj.cantidad)
    }

    anio_actual = data['anio_id']
    anio_anterior = anio_actual - 1

    if data['mes_id'] == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = data['mes_id'] - 1
        anio_intermensual = anio_actual

    data_intermensual = get_model_cantidades_privado(
        mes=mes_anterior,
        anio=anio_intermensual,
        valor=data['valor_id'],
        tipo=data['tipo'],
        estacionalidad=data['estacionalidad_id']
    )

    data_interanual = get_model_cantidades_privado(
        mes=data['mes_id'],
        anio=anio_anterior,
        valor=data['valor_id'],
        tipo=data['tipo'],
        estacionalidad=data['estacionalidad_id']
    )

    var_intermensual = var_interanual = 0.0
    dif_intermensual = dif_interanual = 0.0

    if data_intermensual and float(data_intermensual['cantidad']) != 0:
        prev = float(data_intermensual['cantidad'])
        var_intermensual = (data['cantidad'] / prev) * 100 - 100
        dif_intermensual = data['cantidad'] - prev

    if data_interanual and float(data_interanual['cantidad']) != 0:
        prev = float(data_interanual['cantidad'])
        var_interanual = (data['cantidad'] / prev) * 100 - 100
        dif_interanual = data['cantidad'] - prev

    IndicadoresPrivado.objects.update_or_create(
        tipo=obj.tipo,
        estacionalidad=obj.estacionalidad,
        anio=obj.anio,
        mes=obj.mes,
        valor=obj.valor,
        defaults={
            "variacion_interanual": round(var_interanual, 1),
            "variacion_intermensual": round(var_intermensual, 1),
            "diferencia_interanual": round(dif_interanual, 1),
            "diferencia_intermensual": round(dif_intermensual, 1),
        }
    )


@receiver(post_save, sender=CantidadesPrivado)
def total_post_save(sender, instance, created, **kwargs):
    calcular_y_guardar_variacion(instance)


# ============================================================
# --- CÁLCULO VARIACIONES: RemuneracionRama ---
# ============================================================

def get_remuneracion_rama(mes, anio, valor, rama, estacionalidad):
    return RemuneracionRama.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        rama_id=rama,
        estacionalidad_id=estacionalidad
    ).values("remuneracion").first()


def calcular_y_guardar_variacion_remuneracion(obj):

    data = {
        'rama_id': obj.rama.id,
        'estacionalidad_id': obj.estacionalidad.id,
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'remuneracion': float(obj.remuneracion)
    }

    anio_actual = data['anio_id']
    anio_anterior = anio_actual - 1

    if data['mes_id'] == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = data['mes_id'] - 1
        anio_intermensual = anio_actual

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

    var_intermensual = var_interanual = 0.0

    if data_intermensual and float(data_intermensual['remuneracion']) != 0:
        prev = float(data_intermensual['remuneracion'])
        var_intermensual = (data['remuneracion'] / prev) * 100 - 100

    if data_interanual and float(data_interanual['remuneracion']) != 0:
        prev = float(data_interanual['remuneracion'])
        var_interanual = (data['remuneracion'] / prev) * 100 - 100

    RemuneracionRama.objects.filter(pk=obj.pk).update(
        variacion_intermensual=round(var_intermensual, 1),
        variacion_interanual=round(var_interanual, 1)
    )


@receiver(post_save, sender=RemuneracionRama)
def recalcular_variacion_remuneracion(sender, instance, created, **kwargs):
    calcular_y_guardar_variacion_remuneracion(instance)


# ============================================================
# --- ADMIN ---
# ============================================================

@admin.register(CantidadesPrivado)
class CantidadesPrivadoAdmin(admin.ModelAdmin):
    form = CantidadesPrivadoAdminForm
    list_filter = ['tipo__tipo', 'anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['tipo', 'estacionalidad', 'anio', 'mes', 'valor', 'cantidad']
    list_editable = ['estacionalidad', 'anio', 'mes', 'valor', 'cantidad']
    list_per_page = 12


@admin.register(RemuneracionRama)
class RemuneracionRamaAdmin(admin.ModelAdmin):
    form = RemuneracionRamaAdminForm
    list_filter = ['rama__rama', 'anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['rama', 'anio', 'mes', 'valor', 'remuneracion',
                    'variacion_interanual', 'variacion_intermensual']
    exclude = ['variacion_interanual', 'variacion_intermensual']
    list_per_page = 12