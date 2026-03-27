from django.contrib import admin
from django import forms
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TipoGanado, FaenaPecuario, StockPecuario, ConsumoCapita, ConsumoTotalProteina


# ============================================================
# FORMULARIOS CON VALIDACIONES
# ============================================================

class FaenaPecuarioForm(forms.ModelForm):
    class Meta:
        model = FaenaPecuario
        fields = '__all__'

    

class StockPecuarioForm(forms.ModelForm):
    class Meta:
        model = StockPecuario
        fields = '__all__'

   


class ConsumoCapitaForm(forms.ModelForm):
    class Meta:
        model = ConsumoCapita
        fields = '__all__'

   
# ============================================================
# LÓGICA: CONSUMO TOTAL PROTEÍNA
# ============================================================

def calcular_consumo_total(anio, mes, valor):
    """
    Suma el consumo de todos los TipoGanado para un anio+mes+valor dado.
    Solo crea/actualiza ConsumoTotalProteina si están cargados TODOS los tipos.
    """
    tipos_existentes = set(TipoGanado.objects.values_list('id', flat=True))

    if not tipos_existentes:
        return

    registros = ConsumoCapita.objects.filter(anio=anio, mes=mes, valor=valor)
    tipos_cargados = set(registros.values_list('tipo_ganado_id', flat=True))

    # Solo calcular si todos los tipos de ganado están presentes
    if not tipos_existentes.issubset(tipos_cargados):
        return

    total = sum(float(r.consumo) for r in registros)

    ConsumoTotalProteina.objects.update_or_create(
        anio=anio,
        mes=mes,
        valor=valor,
        defaults={'consumo_total': round(total, 2)}
    )


@receiver(post_save, sender=ConsumoCapita)
def actualizar_consumo_total(sender, instance, **kwargs):
    calcular_consumo_total(instance.anio, instance.mes, instance.valor)


@receiver(post_delete, sender=ConsumoCapita)
def recalcular_consumo_total_al_borrar(sender, instance, **kwargs):
    # Si se elimina un registro, el total ya no es válido → eliminar
    ConsumoTotalProteina.objects.filter(
        anio=instance.anio,
        mes=instance.mes,
        valor=instance.valor
    ).delete()


# ============================================================
# ADMIN
# ============================================================

@admin.register(TipoGanado)
class TipoGanadoAdmin(admin.ModelAdmin):
    list_display = ['tipo_ganado']
    search_fields = ['tipo_ganado']


@admin.register(FaenaPecuario)
class FaenaPecuarioAdmin(admin.ModelAdmin):
    form = FaenaPecuarioForm
    list_display = ['anio', 'mes', 'valor', 'tipo_ganado', 'cabezas']
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo_ganado__tipo_ganado']
    ordering = ['-anio', 'mes']
    list_per_page = 20


@admin.register(StockPecuario)
class StockPecuarioAdmin(admin.ModelAdmin):
    form = StockPecuarioForm
    list_display = ['anio', 'mes', 'valor', 'tipo_ganado', 'stock', 'fecha_carga']
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo_ganado__tipo_ganado']
    ordering = ['-anio', 'mes']
    list_per_page = 20


@admin.register(ConsumoCapita)
class ConsumoCapitaAdmin(admin.ModelAdmin):
    form = ConsumoCapitaForm
    list_display = ['anio', 'mes', 'valor', 'tipo_ganado', 'consumo', 'fecha_carga']
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo_ganado__tipo_ganado']
    ordering = ['-anio', 'mes']
    list_per_page = 20


@admin.register(ConsumoTotalProteina)
class ConsumoTotalProteinaAdmin(admin.ModelAdmin):
    list_display = ['anio', 'mes', 'valor', 'consumo_total', 'fecha_carga']
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_per_page = 20
    readonly_fields = ['anio', 'mes', 'valor', 'consumo_total', 'fecha_carga']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
