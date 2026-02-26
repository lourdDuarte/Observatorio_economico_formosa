from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
import re


# =====================================================
# FORM VALIDACIÓN
# =====================================================

class PatentamientoIndicadorAdminForm(forms.ModelForm):
    class Meta:
        model = Indicadores
        fields = "__all__"

    def clean_total(self):
        valor = self.cleaned_data.get("total")

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

def get_indicador_data(mes, anio, valor, movimiento, tipo_vehiculo):
    return Indicadores.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        movimiento_vehicular_id=movimiento,
        tipo_vehiculo_id=tipo_vehiculo
    ).first()


# =====================================================
# CÁLCULOS (CORREGIDOS A FLOAT)
# =====================================================

def calcular_valores(obj):

    total_actual = float(obj.total)
    mes_actual = obj.mes.id
    anio_actual = obj.anio.id

    # -------------------
    # TOTAL ACUMULADO
    # -------------------
    total_acumulado = total_actual

    if mes_actual > 1:
        indicador_anterior = get_indicador_data(
            mes=mes_actual - 1,
            anio=anio_actual,
            valor=obj.valor.id,
            movimiento=obj.movimiento_vehicular.id,
            tipo_vehiculo=obj.tipo_vehiculo.id
        )

        if indicador_anterior and indicador_anterior.total_acumulado:
            total_acumulado += float(indicador_anterior.total_acumulado)

    # -------------------
    # INTERMENSUAL
    # -------------------
    if mes_actual == 1:
        mes_anterior_intermensual = 12
        anio_anterior_intermensual = anio_actual - 1
    else:
        mes_anterior_intermensual = mes_actual - 1
        anio_anterior_intermensual = anio_actual

    var_intermensual = 0.0

    data_intermensual = get_indicador_data(
        mes=mes_anterior_intermensual,
        anio=anio_anterior_intermensual,
        valor=obj.valor.id,
        movimiento=obj.movimiento_vehicular.id,
        tipo_vehiculo=obj.tipo_vehiculo.id
    )

    if data_intermensual and float(data_intermensual.total) != 0:
        var_intermensual = (
            total_actual / float(data_intermensual.total)
        ) * 100 - 100

    # -------------------
    # INTERANUAL
    # -------------------
    var_interanual = 0.0

    data_interanual = get_indicador_data(
        mes=mes_actual,
        anio=anio_actual - 1,
        valor=obj.valor.id,
        movimiento=obj.movimiento_vehicular.id,
        tipo_vehiculo=obj.tipo_vehiculo.id
    )

    if data_interanual and float(data_interanual.total) != 0:
        var_interanual = (
            total_actual / float(data_interanual.total)
        ) * 100 - 100

    return {
        'total_acumulado': str(round(total_acumulado, 2)),
        'variacion_intermensual': str(round(var_intermensual, 1)),
        'variacion_interanual': str(round(var_interanual, 1)),
    }


# =====================================================
# SIGNAL
# =====================================================

@receiver(post_save, sender=Indicadores)
def indicadores_post_save_handler(sender, instance, **kwargs):

    valores_actuales = calcular_valores(instance)

    Indicadores.objects.filter(pk=instance.pk).update(
        total_acumulado=valores_actuales['total_acumulado'],
        variacion_intermensual=valores_actuales['variacion_intermensual'],
        variacion_interanual=valores_actuales['variacion_interanual']
    )

    posteriores = Indicadores.objects.filter(
        anio=instance.anio,
        valor=instance.valor,
        movimiento_vehicular=instance.movimiento_vehicular,
        tipo_vehiculo=instance.tipo_vehiculo,
        mes__id__gt=instance.mes.id
    ).order_by('mes__id')

    acumulado = float(valores_actuales['total_acumulado'])

    for indicador in posteriores:

        acumulado += float(indicador.total)

        valores = calcular_valores(indicador)
        valores['total_acumulado'] = str(round(acumulado, 2))

        Indicadores.objects.filter(pk=indicador.pk).update(
            total_acumulado=valores['total_acumulado'],
            variacion_intermensual=valores['variacion_intermensual'],
            variacion_interanual=valores['variacion_interanual']
        )

    siguiente_anio = get_indicador_data(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        valor=instance.valor.id,
        movimiento=instance.movimiento_vehicular.id,
        tipo_vehiculo=instance.tipo_vehiculo.id
    )

    if siguiente_anio:
        valores_siguiente_anio = calcular_valores(siguiente_anio)

        Indicadores.objects.filter(pk=siguiente_anio.pk).update(
            total_acumulado=valores_siguiente_anio['total_acumulado'],
            variacion_intermensual=valores_siguiente_anio['variacion_intermensual'],
            variacion_interanual=valores_siguiente_anio['variacion_interanual']
        )


# =====================================================
# ADMIN
# =====================================================

@admin.register(Indicadores)
class PatentamientoIndicadorAdmin(admin.ModelAdmin):

    form = PatentamientoIndicadorAdminForm

    list_filter = ['anio__anio', 'mes__mes', 'movimiento_vehicular',
                   'tipo_vehiculo__tipo_vehiculo', 'valor__valor']

    search_fields = ['total']

    ordering = ['-anio', 'mes']

    list_display = ['movimiento_vehicular', 'tipo_vehiculo', 'anio', 'mes',
                    'valor', 'total', 'total_acumulado',
                    'variacion_interanual', 'variacion_intermensual']

    list_editable = ['tipo_vehiculo', 'valor', 'total']

    list_per_page = 12

    exclude = ['total_acumulado',
               'variacion_interanual',
               'variacion_intermensual']