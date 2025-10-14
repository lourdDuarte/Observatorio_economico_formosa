from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Indicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    
    list_filter = [ 'anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = [
        'anio', 'mes', 'valor', 
        'variacion_intermensual',
        'variacion_interanual', 
        
    ]
    list_editable = [
        'mes', 'valor',
        'variacion_intermensual','variacion_interanual', 
        
    ]
    list_per_page = 12

@admin.register(Indicadores_division)
class IndicadoresDivisionAdmin(admin.ModelAdmin):
    
    list_filter = [ 'anio__anio', 'mes__mes', 'valor__valor', 'divisionIpc']
    ordering = ['-anio', 'mes']
    list_display = [
        'divisionIpc', 'anio', 'mes', 'valor', 
        'variacion_intermensual',
        'variacion_interanual', 
        
    ]
    list_editable = [
        'anio','mes', 'valor',
        'variacion_intermensual','variacion_interanual', 
        
    ]
    list_per_page = 12

@admin.register(TipoDivision)
class TipoDivisionAdmin(admin.ModelAdmin):
    
    list_filter = [ 'tipo_division']
    
    list_display = [
        'tipo_division'
        
    ]

    list_per_page = 12