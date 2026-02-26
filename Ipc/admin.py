from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import *
import re


# =====================================================
# FORM VALIDACIÓN INDICADORES
# =====================================================

class IndicadoresAdminForm(forms.ModelForm):
    class Meta:
        model = Indicadores
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        intermensual = cleaned_data.get("variacion_intermensual")
        interanual = cleaned_data.get("variacion_interanual")

        for campo, valor in {
            "variacion_intermensual": intermensual,
            "variacion_interanual": interanual
        }.items():

            if valor is None:
                continue

            valor_str = str(valor)

            if not re.fullmatch(r'^-?\d+(\.\d+)?$', valor_str):
                self.add_error(
                    campo,
                    "Solo se permiten números con punto decimal (ej: 4.5 o -2.3). No use comas ni símbolos."
                )

        return cleaned_data


# =====================================================
# FORM VALIDACIÓN INDICADORES DIVISION
# =====================================================

class IndicadoresDivisionAdminForm(forms.ModelForm):
    class Meta:
        model = Indicadores_division
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        intermensual = cleaned_data.get("variacion_intermensual")
        interanual = cleaned_data.get("variacion_interanual")

        for campo, valor in {
            "variacion_intermensual": intermensual,
            "variacion_interanual": interanual
        }.items():

            if valor is None:
                continue

            valor_str = str(valor)

            if not re.fullmatch(r'^-?\d+(\.\d+)?$', valor_str):
                self.add_error(
                    campo,
                    "Solo se permiten números con punto decimal (ej: 4.5 o -2.3). No use comas ni símbolos."
                )

        return cleaned_data


# =====================================================
# ADMIN
# =====================================================

@admin.register(Indicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    form = IndicadoresAdminForm

    list_filter = ['anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = [
        'anio', 'mes', 'valor',
        'variacion_intermensual',
        'variacion_interanual',
    ]
    list_editable = [
        'mes', 'valor',
        'variacion_intermensual',
        'variacion_interanual',
    ]
    list_per_page = 12


@admin.register(Indicadores_division)
class IndicadoresDivisionAdmin(admin.ModelAdmin):
    form = IndicadoresDivisionAdminForm

    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'divisionIpc']
    ordering = ['-anio', 'mes']
    list_display = [
        'divisionIpc', 'anio', 'mes', 'valor',
        'variacion_intermensual',
        'variacion_interanual',
    ]
    list_editable = [
        'anio', 'mes', 'valor',
        'variacion_intermensual',
        'variacion_interanual',
    ]
    list_per_page = 12


@admin.register(TipoDivision)
class TipoDivisionAdmin(admin.ModelAdmin):

    list_filter = ['tipo_division']

    list_display = [
        'tipo_division'
    ]

    list_per_page = 12