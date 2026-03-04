from django.contrib import admin
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
import re


# ============================================================
# VALIDACIÓN NUMÉRICA
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
            f"{nombre_campo}: Solo se permiten números con punto decimal opcional."
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
# FUNCIONES AUXILIARES
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
# CÁLCULO VARIACIONES CantidadesPrivado
# ============================================================

def calcular_y_guardar_variacion(obj):

    cantidad_actual = float(obj.cantidad or 0)

    anio_actual = obj.anio.id
    anio_anterior = anio_actual - 1

    if obj.mes.id == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = obj.mes.id - 1
        anio_intermensual = anio_actual

    data_intermensual = get_model_cantidades_privado(
        mes=mes_anterior,
        anio=anio_intermensual,
        valor=obj.valor.id,
        tipo=obj.tipo,
        estacionalidad=obj.estacionalidad.id
    )

    data_interanual = get_model_cantidades_privado(
        mes=obj.mes.id,
        anio=anio_anterior,
        valor=obj.valor.id,
        tipo=obj.tipo,
        estacionalidad=obj.estacionalidad.id
    )

    var_intermensual = var_interanual = 0.0
    dif_intermensual = dif_interanual = 0.0

    if data_intermensual and float(data_intermensual["cantidad"]) != 0:

        cantidad_prev = float(data_intermensual["cantidad"])

        var_intermensual = (cantidad_actual / cantidad_prev) * 100 - 100
        dif_intermensual = cantidad_actual - cantidad_prev

    if data_interanual and float(data_interanual["cantidad"]) != 0:

        cantidad_prev = float(data_interanual["cantidad"])

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


# ============================================================
# SIGNAL CantidadesPrivado
# ============================================================

@receiver(post_save, sender=CantidadesPrivado)
def total_post_save(sender, instance, created, **kwargs):

    def recalcular(obj):
        if obj:
            calcular_y_guardar_variacion(obj)

    # registro actual
    recalcular(instance)

    # ======================
    # MES SIGUIENTE
    # ======================

    if instance.mes.id == 12:
        next_mes = 1
        next_anio = instance.anio.id + 1
    else:
        next_mes = instance.mes.id + 1
        next_anio = instance.anio.id

    obj_mes_siguiente = CantidadesPrivado.objects.filter(
        mes_id=next_mes,
        anio_id=next_anio,
        valor_id=instance.valor.id,
        tipo=instance.tipo,
        estacionalidad=instance.estacionalidad
    ).first()

    recalcular(obj_mes_siguiente)

    # ======================
    # AÑO SIGUIENTE
    # ======================

    obj_anio_siguiente = CantidadesPrivado.objects.filter(
        mes_id=instance.mes.id,
        anio_id=instance.anio.id + 1,
        valor_id=instance.valor.id,
        tipo=instance.tipo,
        estacionalidad=instance.estacionalidad
    ).first()

    recalcular(obj_anio_siguiente)


# ============================================================
# ADMIN
# ============================================================

@admin.register(CantidadesPrivado)
class CantidadesPrivadoAdmin(admin.ModelAdmin):

    form = CantidadesPrivadoAdminForm

    list_filter = ['tipo__tipo', 'anio__anio', 'mes__mes', 'valor__valor']

    ordering = ['-anio', 'mes']

    list_display = [
        'tipo',
        'estacionalidad',
        'anio',
        'mes',
        'valor',
        'cantidad'
    ]

    list_editable = [
        'estacionalidad',
        'anio',
        'mes',
        'valor',
        'cantidad'
    ]

    list_per_page = 12


@admin.register(AsalariadoRama)
class AsalariadoRamaPrivadoAdmin(admin.ModelAdmin):

    list_filter = ['rama__rama', 'trimestre__trimestre', 'valor__valor', 'anio__anio']

    ordering = ['-anio', 'mes']

    list_display = [
        'rama',
        'trimestre',
        'anio',
        'mes',
        'valor',
        'cantidad'
    ]

    list_editable = [
        'trimestre',
        'anio',
        'mes',
        'valor',
        'cantidad'
    ]

    list_per_page = 12


@admin.register(IndicadoresPrivado)
class IndicadoresPrivadoAdmin(admin.ModelAdmin):

    list_filter = ['tipo__tipo', 'anio__anio', 'mes__mes', 'valor__valor']

    ordering = ['-anio', 'mes']

    list_display = [
        'tipo',
        'anio',
        'mes',
        'valor',
        'variacion_interanual',
        'variacion_intermensual',
        'diferencia_intermensual',
        'diferencia_interanual'
    ]

    list_editable = [
        'mes',
        'valor',
        'variacion_interanual',
        'variacion_intermensual',
        'diferencia_intermensual',
        'diferencia_interanual'
    ]

    list_per_page = 12