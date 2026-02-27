# admin.py
from django.contrib import admin
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
import re


# ============================================================
# VALIDACIÓN NUMÉRICA (solo números con punto decimal)
# ============================================================

NUMERIC_REGEX = re.compile(r"^-?\d+(\.\d+)?$")


def validar_numero(valor, nombre_campo):
    if valor is None or valor == "":
        return

    valor_str = str(valor).strip()

    if "," in valor_str:
        raise forms.ValidationError(
            f"{nombre_campo}: No se permite coma. Use punto decimal (ej: 4526.12)."
        )

    if not NUMERIC_REGEX.fullmatch(valor_str):
        raise forms.ValidationError(
            f"{nombre_campo}: Solo se permiten números (con punto decimal opcional)."
        )


# ============================================================
# FORM CantidadesPrivado
# ============================================================

class CantidadesPrivadoAdminForm(forms.ModelForm):
    class Meta:
        model = CantidadesPrivado
        fields = "__all__"

    def clean_cantidad(self):
        valor = self.cleaned_data.get("cantidad")
        validar_numero(valor, "Cantidad")
        return valor


# ============================================================
# FORM RemuneracionRama
# ============================================================

class RemuneracionRamaAdminForm(forms.ModelForm):
    class Meta:
        model = RemuneracionRama
        fields = "__all__"

    def clean_remuneracion(self):
        valor = self.cleaned_data.get("remuneracion")
        validar_numero(valor, "Remuneración")
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

    data_indicadores = {
        'tipo': obj.tipo,
        'estacionalidad_id': obj.estacionalidad.id,
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'cantidad': float(obj.cantidad)
    }

    anio_actual = data_indicadores['anio_id']
    anio_anterior = anio_actual - 1

    if data_indicadores['mes_id'] == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = data_indicadores['mes_id'] - 1
        anio_intermensual = anio_actual

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

    var_intermensual = var_interanual = 0.0
    dif_intermensual = dif_interanual = 0.0

    if data_intermensual and float(data_intermensual['cantidad']) != 0:
        cantidad_prev = float(data_intermensual['cantidad'])
        cantidad_actual = data_indicadores['cantidad']
        var_intermensual = (cantidad_actual / cantidad_prev) * 100 - 100
        dif_intermensual = cantidad_actual - cantidad_prev

    if data_interanual and float(data_interanual['cantidad']) != 0:
        cantidad_prev = float(data_interanual['cantidad'])
        cantidad_actual = data_indicadores['cantidad']
        var_interanual = (cantidad_actual / cantidad_prev) * 100 - 100
        dif_interanual = cantidad_actual - cantidad_prev

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
        var_intermensual = (data['remuneracion'] / float(data_intermensual['remuneracion'])) * 100 - 100

    if data_interanual and float(data_interanual['remuneracion']) != 0:
        var_interanual = (data['remuneracion'] / float(data_interanual['remuneracion'])) * 100 - 100

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


@admin.register(AsalariadoRama)
class AsalariadoRamaPrivadoAdmin(admin.ModelAdmin):
    list_filter = ['rama__rama', 'trimestre__trimestre', 'valor__valor', 'anio__anio']
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


# @admin.register(RemuneracionRama)
# class RemuneracionRamaAdmin(admin.ModelAdmin):
#     form = RemuneracionRamaAdminForm
#     list_filter = ['rama__rama', 'anio__anio', 'mes__mes', 'valor__valor']
#     ordering = ['-anio', 'mes']
#     list_display = ['rama', 'anio', 'mes', 'valor', 'remuneracion',
#                     'variacion_interanual', 'variacion_intermensual']
#     list_editable = ['anio', 'mes', 'valor', 'remuneracion',
#                      'variacion_interanual', 'variacion_intermensual']
#     exclude = ['variacion_interanual', 'variacion_intermensual']
#     list_per_page = 12