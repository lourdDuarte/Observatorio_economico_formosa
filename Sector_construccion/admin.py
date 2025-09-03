from django.contrib import admin
from .models import * 
from .utils import ConstruccionProcessor
from Anio.models import Anio
from Mes.models import Mes 
from Valor.models import Valor  # Asegúrate de importar tu modelo
from django.db.models import QuerySet

# Register your models here.
#@admin.register(Indicadores)
class SectorConstruccionIndicadoresAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor', 'tipo_dato']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'valor',  'mes', 'tipo_dato', 'variacion_interanual', 'variacion_intermensual']
    list_editable = ['valor',  'mes', 'tipo_dato', 'variacion_interanual', 'variacion_intermensual'] 
    list_per_page = 12

   
#@admin.register(SectorConstruccion)
class SectorConstruccionAdmin(admin.ModelAdmin):  # Renombrado para evitar confusión
    search_fields = ['anio__anio', 'valor__valor',  'mes__mes', 'total_empresas', 'total_puesto_trabajo','salario_promedio']
    list_filter = ['anio__anio', 'mes__mes', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'valor',  'mes', 'total_empresas', 'total_puesto_trabajo','salario_promedio']
    list_editable = ['valor',  'mes','total_empresas', 'total_puesto_trabajo','salario_promedio'] 
    list_per_page = 12
    
    def save_model(self, request, obj, form, change):
        
        # Primero, convierte el set a una lista.
        data_indicadores = {
            'anio_id': obj.anio.id,
            'mes_id': obj.mes.id,
            'valor_id': obj.valor.id,
            'total_empresas': obj.total_empresas,
            'total_puesto_trabajo': obj.total_puesto_trabajo,
            'salario_promedio': obj.salario_promedio
        }

        indicador_intermensual = {}
        indicador_interanual = {}
        anio_anterior = int(data_indicadores['anio_id']) - 1

        if data_indicadores['mes_id'] == 1: 
            mes_anterior = 12
            data_intermensual = ConstruccionProcessor.get_data_model_sector_construccion(
            mes_id=mes_anterior, 
            anio_id=anio_anterior, 

            valor_id=data_indicadores['valor_id'])
        else:
            mes_anterior = int(data_indicadores['mes_id']) - 1 # se va utilizar para var intermensual
            data_intermensual = ConstruccionProcessor.get_data_model_sector_construccion(
                mes_id=mes_anterior, 
                anio_id=data_indicadores['anio_id'], 
                valor_id=data_indicadores['valor_id'])
        

        data_interanual = ConstruccionProcessor.get_data_model_sector_construccion(
            mes_id=data_indicadores['mes_id'], 
            anio_id=anio_anterior, 
            valor_id=data_indicadores['valor_id']
        )
                
        
        
        for data in data_intermensual:
            indicador_intermensual = {
                
                'total_puesto_trabajo': data['total_puesto_trabajo'],
                'salario_promedio': data['salario_promedio'],
            }

        for data in data_interanual:
            indicador_interanual = {
                
                'total_puesto_trabajo': data['total_puesto_trabajo'],
                'salario_promedio': data['salario_promedio'],
            }

        var_intermensual = int(data_indicadores['total_puesto_trabajo'])/int(indicador_intermensual['total_puesto_trabajo'])*100-100
        var_interanual = int(data_indicadores['total_puesto_trabajo'])/int(indicador_interanual['total_puesto_trabajo'])*100-100
            
        Indicadores.objects.update_or_create(
                anio=Anio.objects.get(pk= data_indicadores['anio_id']),
                mes=Mes.objects.get(pk=data_indicadores['mes_id']),
                valor=Valor.objects.get(pk=data_indicadores['valor_id']),
                tipo_dato=TipoDato.objects.get(pk=1),
                   
                defaults={
                    "variacion_intermensual": round(var_intermensual, 1),
                    "variacion_interanual": round(var_interanual, 1),
                }
                
            )
            
       
        
        # Llama al método original para guardar el objeto
        super().save_model(request, obj, form, change)