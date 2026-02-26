from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
import re


# =========================================================
# FORM DE VALIDACIÓN (SOLO NÚMEROS CON PUNTO DECIMAL)
# =========================================================

class RecaudacionAdminForm(forms.ModelForm):
    class Meta:
        model = Recaudacion
        fields = "__all__"

    def clean_recaudacion(self):
        valor = self.cleaned_data.get("recaudacion")

        if valor is None:
            raise ValidationError("Este campo no puede estar vacío.")

        valor_str = str(valor)

        if not re.fullmatch(r'^\d+(\.\d+)?$', valor_str):
            raise ValidationError(
                "Solo se permiten números con punto decimal (ej: 4526.12). No use comas ni símbolos."
            )

        return valor


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def get_recaudacion(mes, anio, valor, tipo):
    return Recaudacion.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipo_id=tipo
    ).first()


def get_indicador(mes, anio, valor, tipo):
    return Indicadores.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipo_id=tipo
    ).first()


# =========================================================
# FUNCIÓN CENTRAL DE CÁLCULO (CORREGIDA A FLOAT)
# =========================================================

def calcular_valores(obj):

    recaudacion_actual = float(obj.recaudacion)
    mes_actual = obj.mes.id
    anio_actual = obj.anio.id

    # -----------------------------
    # ACUMULADA
    # -----------------------------
    recaudacion_acumulada = recaudacion_actual

    if mes_actual > 1:
        recaudacion_anterior = get_recaudacion(
            mes=mes_actual - 1,
            anio=anio_actual,
            valor=obj.valor.id,
            tipo=obj.tipo.id
        )

        if recaudacion_anterior and recaudacion_anterior.recaudacion_acumulada:
            recaudacion_acumulada += float(recaudacion_anterior.recaudacion_acumulada)

    # -----------------------------
    # INTERMENSUAL
    # -----------------------------
    if mes_actual == 1:
        mes_anterior = 12
        anio_anterior = anio_actual - 1
    else:
        mes_anterior = mes_actual - 1
        anio_anterior = anio_actual

    var_intermensual = 0.0

    data_intermensual = get_recaudacion(
        mes=mes_anterior,
        anio=anio_anterior,
        valor=obj.valor.id,
        tipo=obj.tipo.id
    )

    if data_intermensual and float(data_intermensual.recaudacion) != 0:
        var_intermensual = (
            recaudacion_actual / float(data_intermensual.recaudacion)
        ) * 100 - 100

    # -----------------------------
    # INTERANUAL
    # -----------------------------
    var_interanual = 0.0

    data_interanual = get_recaudacion(
        mes=mes_actual,
        anio=anio_actual - 1,
        valor=obj.valor.id,
        tipo=obj.tipo.id
    )

    if data_interanual and float(data_interanual.recaudacion) != 0:
        var_interanual = (
            recaudacion_actual / float(data_interanual.recaudacion)
        ) * 100 - 100

    return {
        'recaudacion_acumulada': str(round(recaudacion_acumulada, 2)),
        'variacion_intermensual': str(round(var_intermensual, 1)),
        'variacion_interanual': str(round(var_interanual, 1)),
    }


# =========================================================
# SIGNAL POST SAVE
# =========================================================

@receiver(post_save, sender=Recaudacion)
def recaudacion_post_save_handler(sender, instance, **kwargs):

    valores_actuales = calcular_valores(instance)

    Recaudacion.objects.filter(pk=instance.pk).update(
        recaudacion_acumulada=valores_actuales['recaudacion_acumulada']
    )

    indicador, created = Indicadores.objects.get_or_create(
        anio=instance.anio,
        mes=instance.mes,
        valor=instance.valor,
        tipo=instance.tipo,
        defaults={
            'variacion_intermensual': valores_actuales['variacion_intermensual'],
            'variacion_interanual': valores_actuales['variacion_interanual'],
        }
    )

    if not created:
        Indicadores.objects.filter(pk=indicador.pk).update(
            variacion_intermensual=valores_actuales['variacion_intermensual'],
            variacion_interanual=valores_actuales['variacion_interanual']
        )

    # -----------------------------
    # RECALCULAR MESES POSTERIORES
    # -----------------------------

    posteriores = Recaudacion.objects.filter(
        anio=instance.anio,
        valor=instance.valor,
        tipo=instance.tipo,
        mes__id__gt=instance.mes.id
    ).order_by('mes__id')

    acumulado = float(valores_actuales['recaudacion_acumulada'])

    for rec in posteriores:

        acumulado += float(rec.recaudacion)

        valores = calcular_valores(rec)
        valores['recaudacion_acumulada'] = str(round(acumulado, 2))

        Recaudacion.objects.filter(pk=rec.pk).update(
            recaudacion_acumulada=valores['recaudacion_acumulada']
        )

        indicador_posterior, _ = Indicadores.objects.get_or_create(
            anio=rec.anio,
            mes=rec.mes,
            valor=rec.valor,
            tipo=rec.tipo
        )

        Indicadores.objects.filter(pk=indicador_posterior.pk).update(
            variacion_intermensual=valores['variacion_intermensual'],
            variacion_interanual=valores['variacion_interanual']
        )

    # -----------------------------
    # RECALCULAR MISMO MES AÑO SIGUIENTE
    # -----------------------------

    siguiente_anio = get_recaudacion(
        mes=instance.mes.id,
        anio=instance.anio.id + 1,
        valor=instance.valor.id,
        tipo=instance.tipo.id
    )

    if siguiente_anio:
        valores_siguiente_anio = calcular_valores(siguiente_anio)

        Recaudacion.objects.filter(pk=siguiente_anio.pk).update(
            recaudacion_acumulada=valores_siguiente_anio['recaudacion_acumulada']
        )

        indicador_next, _ = Indicadores.objects.get_or_create(
            anio=siguiente_anio.anio,
            mes=siguiente_anio.mes,
            valor=siguiente_anio.valor,
            tipo=siguiente_anio.tipo
        )

        Indicadores.objects.filter(pk=indicador_next.pk).update(
            variacion_intermensual=valores_siguiente_anio['variacion_intermensual'],
            variacion_interanual=valores_siguiente_anio['variacion_interanual']
        )


# =========================================================
# ADMIN
# =========================================================

@admin.register(Recaudacion)
class RecaudacionAdmin(admin.ModelAdmin):
    form = RecaudacionAdminForm
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo__tipo']
    search_fields = ['recaudacion']
    ordering = ['-anio', 'mes']
    list_display = ['tipo', 'anio', 'mes', 'valor',
                    'recaudacion', 'recaudacion_acumulada']
    list_editable = ['anio', 'mes', 'valor', 'recaudacion']
    list_per_page = 12
    exclude = ['recaudacion_acumulada']


@admin.register(Indicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo__tipo']
    ordering = ['-anio', 'mes']
    list_display = ['tipo', 'anio', 'mes', 'valor',
                    'variacion_intermensual', 'variacion_interanual']
    list_editable = ['anio', 'mes', 'valor',
                     'variacion_intermensual', 'variacion_interanual']
    list_per_page = 12