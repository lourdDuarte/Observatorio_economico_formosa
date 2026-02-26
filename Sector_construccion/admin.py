from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
import re


# =========================================================
# FORM VALIDACIÓN NUMÉRICA
# =========================================================

class SectorConstruccionAdminForm(forms.ModelForm):
    class Meta:
        model = SectorConstruccion
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        campos = {
            "total_empresas": cleaned_data.get("total_empresas"),
            "total_puesto_trabajo": cleaned_data.get("total_puesto_trabajo"),
            "salario_promedio": cleaned_data.get("salario_promedio"),
        }

        for campo, valor in campos.items():

            if valor is None:
                continue

            valor_str = str(valor)

            if not re.fullmatch(r'^-?\d+(\.\d+)?$', valor_str):
                self.add_error(
                    campo,
                    "Solo se permiten números con punto decimal (ej: 4526.12 o -2.5). No use comas ni símbolos."
                )

        return cleaned_data


# =========================================================
# FUNCIÓN AUXILIAR
# =========================================================

def get_model_total_construccion(mes, anio, valor, tipo_dato):
    qs = SectorConstruccion.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor
    ).values("total_puesto_trabajo", "salario_promedio").first()

    if not qs:
        return None

    if tipo_dato == 1:
        return qs["total_puesto_trabajo"]
    elif tipo_dato == 2:
        return qs["salario_promedio"]

    return None


# =========================================================
# FUNCIÓN PRINCIPAL CÁLCULO
# =========================================================

def calcular_y_guardar_variacion(obj, tipo_dato, campo_valor):

    data_indicadores = {
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'total': float(getattr(obj, campo_valor) or 0)
    }

    anio_anterior = int(data_indicadores['anio_id']) - 1

    # ---------------- INTERMENSUAL ----------------

    if data_indicadores['mes_id'] == 1:
        mes_anterior = 12
        anio_anterior_intermensual = anio_anterior
    else:
        mes_anterior = int(data_indicadores['mes_id']) - 1
        anio_anterior_intermensual = data_indicadores['anio_id']

    data_intermensual = get_model_total_construccion(
        mes=mes_anterior,
        anio=anio_anterior_intermensual,
        valor=data_indicadores['valor_id'],
        tipo_dato=tipo_dato
    )

    # ---------------- INTERANUAL ----------------

    data_interanual = get_model_total_construccion(
        mes=data_indicadores['mes_id'],
        anio=anio_anterior,
        valor=data_indicadores['valor_id'],
        tipo_dato=tipo_dato
    )

    var_intermensual = 0.0
    var_interanual = 0.0

    if data_intermensual and float(data_intermensual) != 0:
        var_intermensual = (
            data_indicadores['total'] / float(data_intermensual)
        ) * 100 - 100

    if data_interanual and float(data_interanual) != 0:
        var_interanual = (
            data_indicadores['total'] / float(data_interanual)
        ) * 100 - 100

    Indicadores.objects.update_or_create(
        anio=obj.anio,
        mes=obj.mes,
        valor=obj.valor,
        tipo_dato_id=tipo_dato,
        defaults={
            "variacion_intermensual": round(var_intermensual, 1),
            "variacion_interanual": round(var_interanual, 1),
        }
    )


# =========================================================
# SIGNAL
# =========================================================

@receiver(post_save, sender=SectorConstruccion)
def sector_construccion_post_save(sender, instance, created, **kwargs):

    campos_tipo_dato = {
        1: "total_puesto_trabajo",
        2: "salario_promedio",
    }

    for tipo_dato, campo_valor in campos_tipo_dato.items():
        calcular_y_guardar_variacion(instance, tipo_dato, campo_valor)

    # ---------------- MES SIGUIENTE ----------------

    if instance.mes.id == 12:
        next_month_obj = SectorConstruccion.objects.filter(
            anio_id=instance.anio.id + 1,
            mes_id=1,
            valor_id=instance.valor.id
        ).first()
    else:
        next_month_obj = SectorConstruccion.objects.filter(
            anio_id=instance.anio.id,
            mes_id=instance.mes.id + 1,
            valor_id=instance.valor.id
        ).first()

    if next_month_obj:
        for tipo_dato, campo_valor in campos_tipo_dato.items():
            calcular_y_guardar_variacion(next_month_obj, tipo_dato, campo_valor)

    # ---------------- MISMO MES AÑO SIGUIENTE ----------------

    next_year_obj = SectorConstruccion.objects.filter(
        anio_id=instance.anio.id + 1,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id
    ).first()

    if next_year_obj:
        for tipo_dato, campo_valor in campos_tipo_dato.items():
            calcular_y_guardar_variacion(next_year_obj, tipo_dato, campo_valor)


# =========================================================
# ADMIN
# =========================================================

@admin.register(SectorConstruccion)
class SectorConstruccionAdmin(admin.ModelAdmin):

    form = SectorConstruccionAdminForm

    search_fields = ['anio__anio', 'mes__mes', 'valor__valor']
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor',
                    'total_empresas',
                    'total_puesto_trabajo',
                    'salario_promedio']
    list_editable = ['total_empresas',
                     'total_puesto_trabajo',
                     'salario_promedio']
    list_per_page = 12


@admin.register(Indicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    search_fields = ['anio__anio', 'mes__mes', 'valor__valor']
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo_dato']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor',
                    'tipo_dato',
                    'variacion_interanual',
                    'variacion_intermensual']
    list_editable = ['mes', 'valor', 'tipo_dato',
                     'variacion_interanual',
                     'variacion_intermensual']
    list_per_page = 12