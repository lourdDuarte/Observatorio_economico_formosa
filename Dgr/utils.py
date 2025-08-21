from Dgr.models import Recaudacion
from django.shortcuts import render
from Mes.models import *
import json
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from collections import defaultdict
from django.db.models import  QuerySet


class DgrDataProcessor:
    DEFAULT_YEAR = 7

  
    @staticmethod
    def get_data_recaudacion(**kwargs) -> dict:
    
        return Recaudacion.objects.select_related('mes', 'anio', 'valor', 'tipo').values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'tipo__tipo',
            'recaudacion'
        ).filter(**kwargs)
    
    @classmethod
    def get_filtered_data(cls, params: Dict[str, Any]) -> QuerySet:
       
        
        if params['is_valid']:
            
            return cls.get_data_recaudacion(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                tipo_id__in=[1,3]
               
               
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_data_recaudacion(
                anio_id=cls.DEFAULT_YEAR,
                tipo_id__in=[1,3]
                
                
            )
        
      
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
        



def diccionario(queryset):
    recaudacion = []
    recaudacion_tributaria = []
    recaudacion_iibb = []
    
    meses = []

    # Para mantener el orden, usamos listas separadas para cada región con su mes
    meses_tributaria = []
    meses_iibb = []

    for item in queryset:
        mes = item['mes__mes'] + " " +  str(item['anio__anio'])
        tipo = item['tipo__tipo']
        recaudacion = (item['recaudacion'])
       

        if tipo == 'Tributaria':
            recaudacion_tributaria.append(recaudacion)
            meses_tributaria.append(mes)
            
        elif tipo == 'IIBB':
            recaudacion_iibb.append(recaudacion)
            
            meses_iibb.append(mes)

    # Obtener la cantidad mínima común
    minimo = min(len(recaudacion_tributaria), len(recaudacion_iibb))

    # Recortar todas las listas al mismo tamaño
    datos = {
        'meses': meses_tributaria[:minimo],  # o meses_nacional[:minimo], ambos deberían coincidir en orden
        'Valor recaudacion Tributaria': recaudacion_tributaria[:minimo],
        'Valor recaudacion IIBB': recaudacion_iibb[:minimo],
        
    }

    return datos


def process_dgr_data(request:HttpRequest, context_keys: Dict[str, str], template: str) -> HttpResponse:
    processor = DgrDataProcessor

    meses = Mes.objects.all()
    params = processor.procces_request_parameters(request)

    data_recaudacion = processor.get_filtered_data(params)

    diccionario_recaudacion = diccionario(data_recaudacion)

     # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_recaudacion']: data_recaudacion,
        context_keys['diccionario_recaudacion']: diccionario_recaudacion,
        'meses': meses,
    }
    
    return render(request, template, context)