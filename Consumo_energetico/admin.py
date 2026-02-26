from django.contrib import admin
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.core.exceptions import ValidationError
import re

# ---------------------------------------------------
# FUNCIONES REFSA
# ---------------------------------------------------

def get_indicador_refsa(mes, anio, valor, tarifa):
    return Refsa.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tarifa_id=tarifa
    ).first()


# ---------------------------------------------------
# FUNCIÓN DE CÁLCULO REFSA
# ---------------------------------------------------

def calcular_variacion_bimestral_interanual(obj):
    # Evitar loop del post_save si se llamara mal en otro lado
    if hasattr(obj, "_skip_signal"):
        return

    data = {
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'tarifa_id': obj.tarifa_id,
        'cantidad_usuarios': float(obj.cantidad_usuarios)
    }

    anio_actual = data['anio_id']
    mes_actual = data['mes_id']
    anio_anterior = anio_actual - 1

    # ---------------------------------------------------
    # 1) DETERMINAR BIMESTRAL (dos meses atrás)
    # ---------------------------------------------------

    if mes_actual == 1:
        mes_bimestral = 11
        anio_bimestral = anio_anterior
    elif mes_actual == 2:
        mes_bimestral = 12
        anio_bimestral = anio_anterior
    else:
        mes_bimestral = mes_actual - 2
        anio_bimestral = anio_actual

    data_bimestral = get_indicador_refsa(
        mes=mes_bimestral,
        anio=anio_bimestral,
        valor=data['valor_id'],
        tarifa=data['tarifa_id']
    )

    # ---------------------------------------------------
    # 2) DETERMINAR INTERANUAL (mismo mes, año anterior)
    # ---------------------------------------------------

    data_interanual = get_indicador_refsa(
        mes=mes_actual,
        anio=anio_anterior,
        valor=data['valor_id'],
        tarifa=data['tarifa_id']
    )

    # ---------------------------------------------------
    # CALCULAR VARIACIONES
    # ---------------------------------------------------

    var_bimestral = 0.0
    var_interanual = 0.0

    if data_bimestral and float(data_bimestral.cantidad_usuarios) != 0:
        var_bimestral = (
            data['cantidad_usuarios'] /
            float(data_bimestral.cantidad_usuarios) * 100
        ) - 100

    if data_interanual and float(data_interanual.cantidad_usuarios) != 0:
        var_interanual = (
            data['cantidad_usuarios'] /
            float(data_interanual.cantidad_usuarios) * 100
        ) - 100

    # ---------------------------------------------------
    # GUARDAR (sin disparar signals porque es .update())
    # ---------------------------------------------------

    obj._skip_signal = True  # flag defensivo

    Refsa.objects.filter(pk=obj.pk).update(
        variacion_bimestral=round(var_bimestral, 1),
        variacion_interanual=round(var_interanual, 1)
    )

    del obj._skip_signal


# ---------------------------------------------------
# SIGNAL POST_SAVE REFSA
# ---------------------------------------------------

@receiver(post_save, sender=Refsa)
def total_post_save_refsa(sender, instance, created, **kwargs):
    if getattr(instance, "_skip_signal", False):
        return

    # Recalcular el registro actual
    calcular_variacion_bimestral_interanual(instance)

    # Calcular mes siguiente
    if instance.mes.id == 12:
        mes_sig = 1
        anio_sig = instance.anio.id + 1
    else:
        mes_sig = instance.mes.id + 1
        anio_sig = instance.anio.id

    sig = Refsa.objects.filter(
        anio_id=anio_sig,
        mes_id=mes_sig,
        valor_id=instance.valor.id,
        tarifa_id=instance.tarifa.id
    ).first()

    if sig:
        calcular_variacion_bimestral_interanual(sig)

    # Calcular mes siguiente + 1 (por la bimestral de los futuros)
    if mes_sig == 12:
        mes_sig2 = 1
        anio_sig2 = anio_sig + 1
    else:
        mes_sig2 = mes_sig + 1
        anio_sig2 = anio_sig

    sig2 = Refsa.objects.filter(
        anio_id=anio_sig2,
        mes_id=mes_sig2,
        valor_id=instance.valor.id,
        tarifa_id=instance.tarifa.id
    ).first()

    if sig2:
        calcular_variacion_bimestral_interanual(sig2)

    # Interanual del año siguiente
    inter = Refsa.objects.filter(
        anio_id=instance.anio.id + 1,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id,
        tarifa_id=instance.tarifa.id
    ).first()

    if inter:
        calcular_variacion_bimestral_interanual(inter)


# ---------------------------------------------------
# FUNCIONES CAMMESA
# ---------------------------------------------------

def get_indicador_cammesa(mes, anio, valor, tarifa):
    return Cammesa.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tarifa_id=tarifa
    ).first()


# ---------------------------------------------------
# FUNCIÓN DE CÁLCULO CAMMESA
# ---------------------------------------------------

def calcular_variacion_intermensual_interanual(obj):
    """
    Calcula y guarda las variaciones intermensuales e interanuales para Cammesa.
    Intermensual: mes actual vs mes anterior.
    Interanual: mismo mes del año anterior.
    """

    # Evitar loop si en algún contexto se reutiliza con flag
    if hasattr(obj, "_skip_signal"):
        return

    data = {
        'anio_id': obj.anio.id,
        'mes_id': obj.mes.id,
        'valor_id': obj.valor.id,
        'tarifa_id': obj.tarifa_id,
        'demanda': float(obj.demanda)
    }

    anio_actual = data['anio_id']
    mes_actual = data['mes_id']
    anio_anterior = anio_actual - 1

    # --- Determinar mes anterior para intermensual ---
    if mes_actual == 1:
        mes_anterior = 12
        anio_intermensual = anio_anterior
    else:
        mes_anterior = mes_actual - 1
        anio_intermensual = anio_actual

    # --- Buscar registro intermensual (mes anterior) ---
    data_intermensual = get_indicador_cammesa(
        mes=mes_anterior,
        anio=anio_intermensual,
        valor=data['valor_id'],
        tarifa=data['tarifa_id']
    )

    # --- Buscar registro interanual (mismo mes año anterior) ---
    data_interanual = get_indicador_cammesa(
        mes=mes_actual,
        anio=anio_anterior,
        valor=data['valor_id'],
        tarifa=data['tarifa_id']
    )

    # --- Inicializar ---
    var_intermensual = 0.0
    var_interanual = 0.0

    # --- Calcular variaciones ---
    if data_intermensual and float(data_intermensual.demanda) != 0:
        var_intermensual = (
            data['demanda'] /
            float(data_intermensual.demanda) * 100
        ) - 100

    if data_interanual and float(data_interanual.demanda) != 0:
        var_interanual = (
            data['demanda'] /
            float(data_interanual.demanda) * 100
        ) - 100

    # ---------------------------------------------------
    # GUARDAR (sin disparar signals porque es .update())
    # ---------------------------------------------------

    obj._skip_signal = True  # evitar recursión

    Cammesa.objects.filter(pk=obj.pk).update(
        variacion_interanual=round(var_interanual, 1),
        variacion_intermensual=round(var_intermensual, 1)
    )

    del obj._skip_signal


# ---------------------------------------------------
# SIGNAL POST_SAVE CAMMESA
# ---------------------------------------------------

@receiver(post_save, sender=Cammesa)
def total_post_save_cammesa(sender, instance, created, **kwargs):

    if getattr(instance, "_skip_signal", False):
        return

    # Recalcular el registro actual
    calcular_variacion_intermensual_interanual(instance)

    # Calcular mes siguiente
    if instance.mes.id == 12:
        mes_sig = 1
        anio_sig = instance.anio.id + 1
    else:
        mes_sig = instance.mes.id + 1
        anio_sig = instance.anio.id

    next_obj = Cammesa.objects.filter(
        anio_id=anio_sig,
        mes_id=mes_sig,
        valor_id=instance.valor.id,
        tarifa_id=instance.tarifa.id
    ).first()

    if next_obj:
        calcular_variacion_intermensual_interanual(next_obj)

    # --- Recalcular mismo mes del año siguiente ---
    next_year_obj = Cammesa.objects.filter(
        anio_id=instance.anio.id + 1,
        mes_id=instance.mes.id,
        valor_id=instance.valor.id,
        tarifa_id=instance.tarifa.id
    ).first()

    if next_year_obj:
        calcular_variacion_intermensual_interanual(next_year_obj)


# ---------------------------------------------------
# ADMIN
# ---------------------------------------------------

admin.site.register(TipoTarifa)
class CammesaAdminForm(forms.ModelForm):
    class Meta:
        model = Cammesa
        fields = "__all__"

    def clean_demanda(self):
        valor = self.cleaned_data.get("demanda")

        if valor is None:
            raise ValidationError("Este campo no puede estar vacío.")

        valor_str = str(valor)

        if not re.fullmatch(r'^\d+(\.\d+)?$', valor_str):
            raise ValidationError(
                "Solo se permiten números con punto decimal (ej: 4526.12). No use comas ni símbolos."
            )

        return valor
    
class RefsaAdminForm(forms.ModelForm):
    class Meta:
        model = Refsa
        fields = "__all__"

    def clean_cantidad_usuarios(self):
        valor = self.cleaned_data.get("cantidad_usuarios")

        if valor is None:
            raise ValidationError("Este campo no puede estar vacío.")

        valor_str = str(valor)

        if not re.fullmatch(r'^\d+(\.\d+)?$', valor_str):
            raise ValidationError(
                "Solo se permiten números con punto decimal (ej: 4526.12). No use comas ni símbolos."
            )

        return valor

@admin.register(Cammesa)
class CammesaAdmin(admin.ModelAdmin):
    form = CammesaAdminForm
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tarifa']
    search_fields = ['demanda']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'tarifa', 'mes', 'valor',
                    'demanda', 'variacion_intermensual', 'variacion_interanual']
    list_editable = ['tarifa', 'mes', 'valor', 'demanda']
    list_per_page = 12
    exclude = ['variacion_intermensual', 'variacion_interanual']


@admin.register(Refsa)
class RefsaAdmin(admin.ModelAdmin):
    form = RefsaAdminForm
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tarifa']
    search_fields = ['cantidad_usuarios']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'tarifa', 'mes', 'valor', 'cantidad_usuarios',
                    'variacion_bimestral', 'variacion_interanual']
    list_editable = ['tarifa', 'mes', 'valor', 'cantidad_usuarios']
    list_per_page = 12
    exclude = ['variacion_bimestral', 'variacion_interanual']