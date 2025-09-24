
from Sector_construccion.models import Indicadores, SectorConstruccion
from django.shortcuts import render
from Mes.models import *
from typing import Dict, Any, Optional
from django.http import HttpRequest, HttpResponse
from Anio.views import *
from collections import defaultdict
from django.db.models import OuterRef, Subquery, QuerySet
import json


class ConstruccionProcessor:

    # Constantes de configuración
    DEFAULT_YEAR = 7

    @staticmethod
    def get_data_model_sector_construccion(**kwargs) -> dict:
        

        
        return SectorConstruccion.objects.select_related('mes', 'anio', 'valor').values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'total_empresas',
            'total_puesto_trabajo',
            'salario_promedio'
        
        ).filter(**kwargs)
    
    @classmethod
    def get_filter_data_model_construccion(cls,  params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
           
            return cls.get_data_model_sector_construccion(
               
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin']).order_by('anio__anio', 'mes__id')
        else:
            
            return cls.get_data_model_sector_construccion(
                anio_id=cls.DEFAULT_YEAR,
                
            ).order_by('anio__anio', 'mes__id')
        
    @classmethod
    def procces_request_parameters(cls, request: HttpRequest,) -> Dict[str,any]:
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')
           

   

            filtros = {}
            if anio_inicio:
                filtros['anio_inicio'] = int(anio_inicio)
            if anio_fin:
                filtros['anio_fin'] = int(anio_fin)
           

           

               
                return {
                    **filtros,
                    'is_valid': True,
                    'error_message': None,
                    
                }   
            else:
                return {
                    **filtros,
                    'is_valid': False,
                    'error_message': None,
                    
                }
        except ValueError:
            return {
                'anio_inicio': None,
                'anio_fin': None,
                'is_valid': False,
                'error_message': "Los filtros ingresados no son válidos."
            }
   

    @staticmethod
    def process_chart_data_totales(value_total, data_variacion: QuerySet) -> Dict[str, list]:
        context_chart_formosa = defaultdict(list)
        context_chart_nacional = defaultdict(list)
       
        for item in data_variacion:
            anio = item['anio__anio']
            total = item[value_total] or 0  # Reemplaza None por 0

            if item['valor__valor'] == 'Formosa':
                context_chart_formosa[anio].append(total)
            elif item['valor__valor'] == 'Nacional':
                context_chart_nacional[anio].append(total)

        return {
            'Formosa': dict(context_chart_formosa),
            'Nacional': dict(context_chart_nacional)
        }
   

class ConstruccionIndicadoresProcessor:
    # Constantes de configuración
    DEFAULT_YEAR = 7

    @staticmethod
    def get_data_model_indicadores_construccion(**kwargs) -> dict:
        

        return Indicadores.objects.select_related('mes', 'anio', 'valor').values(
            'mes__mes',
            'mes',
            'anio__anio',
            'valor__valor',
            'tipo_dato',
            'variacion_interanual',
            'variacion_intermensual'
            
        
        ).filter(**kwargs)
    


    @classmethod
    def get_filter_data_model_indicadores_construccion(cls,tipo_dato:int,  params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
           
            return cls.get_data_model_indicadores_construccion(
                tipo_dato = tipo_dato,
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin']).order_by('anio__anio', 'mes__id')
        else:
            
            return cls.get_data_model_indicadores_construccion(
                tipo_dato = tipo_dato,
                anio_id=cls.DEFAULT_YEAR,
                
            ).order_by('anio__anio', 'mes__id')
        


def diccionario_salario(queryset): 


    formosa_salario_promedio = []
    
    nacional_salario_promedio = []
    

    # Para mantener el orden, usamos listas separadas para cada región con su mes
    meses_formosa = []
    meses_nacional = []

    for item in queryset:
        mes = item['mes__mes'] + " " +  str(item['anio__anio'])
        region = item['valor__valor']
        salario_promedio = float(item['salario_promedio'])
        

        if region == 'Formosa':
            formosa_salario_promedio.append(salario_promedio)
            
            meses_formosa.append(mes)
        elif region == 'Nacional':
            nacional_salario_promedio.append(salario_promedio)
            
            meses_nacional.append(mes)

    # Obtener la cantidad mínima común
    minimo = min(len( formosa_salario_promedio), len(nacional_salario_promedio))

    # Recortar todas las listas al mismo tamaño
    datos = {
        'meses': meses_formosa[:minimo],  # o meses_nacional[:minimo], ambos deberían coincidir en orden
        'Salario promedio Formosa': formosa_salario_promedio[:minimo],
        'Salario promedio Nacional': nacional_salario_promedio[:minimo],
        
    }

    return datos


def diccionario_indicadores(queryset):
    formosa_intermensual = []
    formosa_interanual = []
    nacional_intermensual = []
    nacional_interanual = []
    meses = []

    # Para mantener el orden, usamos listas separadas para cada región con su mes
    meses_formosa = []
    meses_nacional = []

    for item in queryset:
        mes = item['mes__mes'] + " " +  str(item['anio__anio'])
        region = item['valor__valor']
        intermensual = float(item['variacion_intermensual'])
        interanual = float(item['variacion_interanual'])

        if region == 'Formosa':
            formosa_intermensual.append(intermensual)
            formosa_interanual.append(interanual)
            meses_formosa.append(mes)
        elif region == 'Nacional':
            nacional_intermensual.append(intermensual)
            nacional_interanual.append(interanual)
            meses_nacional.append(mes)

    # Obtener la cantidad mínima común
    minimo = min(len(formosa_intermensual), len(nacional_intermensual))

    # Recortar todas las listas al mismo tamaño
    datos = {
        'meses': meses_formosa[:minimo],  # o meses_nacional[:minimo], ambos deberían coincidir en orden
        'Valor intermensual Formosa': formosa_intermensual[:minimo],
        'Valor interanual Formosa': formosa_interanual[:minimo],
        'Valor intermensual Nacional': nacional_intermensual[:minimo],
        'Valor interanual Nacional': nacional_interanual[:minimo],
    }

    return datos




def process_contruccion_salario_data(request:HttpRequest, value_totales:str, context_keys: Dict[str, str], template: str) -> HttpResponse:

    processor = ConstruccionProcessor

    meses = Mes.objects.all()

    params = processor.procces_request_parameters(request)

    data_variacion = processor.get_filter_data_model_construccion(params)
    salario_promedio_diccionario = diccionario_salario(data_variacion)
    context_chart = processor.process_chart_data_totales(value_totales, data_variacion)

     # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['salario_promedio_diccionario']: salario_promedio_diccionario,
        'data_chart_formosa': json.dumps(context_chart['Formosa']),
        'data_chart_nacional': json.dumps(context_chart['Nacional']),
        'meses': meses,
    }
    
    return render(request, template, context)


def process_contruccion_puestos_data(request:HttpRequest,tipo_dato:int, value_totales:str, context_keys: Dict[str, str], template: str) -> HttpResponse:

    processor = ConstruccionIndicadoresProcessor
    construccion = ConstruccionProcessor

    meses = Mes.objects.all()

    params = construccion.procces_request_parameters(request)

    indicador = processor.get_filter_data_model_indicadores_construccion(tipo_dato, params)
    
    
    data_total_puestos = construccion.get_filter_data_model_construccion(params)
    diccionario_variacion_puestos = diccionario_indicadores(processor.get_filter_data_model_indicadores_construccion(tipo_dato, params))
  
    context_chart = construccion.process_chart_data_totales(value_totales, data_total_puestos)

    
    # Convertir a listas normales (si no lo están)
    lista_1 = list(indicador)
    lista_2 = list(data_total_puestos)

    # Crear un diccionario auxiliar para buscar por mes-año-valor
    dict_puestos = {
        (item['anio__anio'], item['mes__mes'], item['valor__valor']): item
        for item in lista_2
    }

    # Unir la información
    data_variacion = []
    for item in lista_1:
        clave = (item['anio__anio'], item['mes__mes'], item['valor__valor'])
        puestos_info = dict_puestos.get(clave, {})  # puede venir vacío si no hay match

        # Crear el nuevo diccionario unificado
        combinado = {
            'anio': item['anio__anio'],
            'mes': item['mes__mes'],
            
            'valor': item['valor__valor'],
            'variacion_intermensual': item.get('variacion_intermensual'),
            'variacion_interanual': item.get('variacion_interanual'),
            'total_puesto_trabajo': puestos_info.get('total_puesto_trabajo'),
        }

        data_variacion.append(combinado)

    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: diccionario_variacion_puestos,
        'data_chart_formosa': json.dumps(context_chart['Formosa']),
        'data_chart_nacional': json.dumps(context_chart['Nacional']),
        'meses': meses,
    }
    
    return render(request, template, context)
