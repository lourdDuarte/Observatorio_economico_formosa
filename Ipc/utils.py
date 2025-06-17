
from Ipc.models import Indicadores
from django.shortcuts import render
from Mes.models import *
from typing import Dict, Any, Optional
from django.http import HttpRequest, HttpResponse
from Anio.views import *
from collections import defaultdict
from django.db.models import OuterRef, Subquery, QuerySet



class IpcProcessor:

    # Constantes de configuración
    DEFAULT_YEAR = 7
   



    @staticmethod
    def get_data_variaciones(**kwargs) -> dict:
        

        
        return Indicadores.objects.select_related('mes', 'anio', 'valor').values(
            'mes__mes',
            'mes',
            'anio__anio',
            'valor__valor',
            'variacion_interanual',
            'variacion_intermensual',
        
        ).filter(**kwargs)


    @classmethod
    def process_and_validate_ipc_data(cls,data):
            meses_vistos = set()  # Almacena pares (mes, año)

            #Validación de Meses Repetidos 
            for item_validacion in data:
                mes_nombre = item_validacion['mes__mes']
                anio = item_validacion['anio__anio']
                valor_tipo = item_validacion['valor__valor']
                
                clave_mes_anio = (mes_nombre, anio)
                
                if clave_mes_anio in meses_vistos:
                    pass
                else:
                    #Mes encontrado por primera vez
                    meses_vistos.add(clave_mes_anio)
            
            grouped_data = defaultdict(lambda: {'NEA': None, 'Nacional': None, 'mes_nombre': None, 'anio': None})

            for item in data:
                mes_id = item['mes']
                mes_nombre = item['mes__mes']
                anio = item['anio__anio']
                valor_tipo = item['valor__valor'] 
                variacion = item['variacion_intermensual']

                clave = (anio, mes_id)

                grouped_data[clave]['mes_nombre'] = mes_nombre
                grouped_data[clave]['anio'] = anio

                if valor_tipo == 'NEA':
                    grouped_data[clave]['NEA'] = variacion
                elif valor_tipo == 'Nacional':
                    grouped_data[clave]['Nacional'] = variacion

            # Armamos la lista final, ordenando por año y mes
            final_chart_data = []

            for clave in sorted(grouped_data.keys()):  # Ordena por (año, mes_id)
                entry = grouped_data[clave]
                if entry['NEA'] is not None and entry['Nacional'] is not None:
                    final_chart_data.append({
                        'mes': f"{entry['mes_nombre']} {entry['anio']}",
                        'variacion_nea': float(entry['NEA']),
                        'variacion_nacional': float(entry['Nacional'])
                    })

            return final_chart_data
    
    @classmethod
    def get_filtered_data(cls, value:int,  params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
            return cls.get_data_variaciones(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                valor_id = value).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_data_variaciones(
                anio_id=cls.DEFAULT_YEAR,
 
            )


    @classmethod
    def procces_request_parameters(cls, request: HttpRequest,) -> Dict[str,any]:
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')
           

            if anio_fin and anio_fin:
                return {
                    'anio_inicio': int(anio_inicio),
                    'anio_fin': int(anio_fin),
                    
                    'is_valid' : True,
                    'error_message': None
                }
            else:
                return {
                    'anio_inicio': None,
                    'anio_fin': None,
                   
                    'is_valid' : False,
                    'error_message': None
                }

        except ValueError:
             return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'valor':None,
                    'is_valid' : False,
                    'error_message': 'Los filtros ingresados no son validos'
                }
        
    


def process_ipc_data(request:HttpRequest, context_keys: Dict[str, str], template: str) -> HttpResponse:
    DEFAULT_VALUE_NEA = 3
    DEFAULT_VALUE_NACION = 2
    meses = Mes.objects.all()

    processor = IpcProcessor
    params = processor.procces_request_parameters(request)


    data_variacion_nea = processor.get_filtered_data(DEFAULT_VALUE_NEA, params)
    data_variacion_nacion = processor.get_filtered_data(DEFAULT_VALUE_NACION,params)
    data_variacion_ipc_table = data_variacion_nea | data_variacion_nacion
   
    final_chart_data = processor.process_and_validate_ipc_data(data_variacion_ipc_table)

       
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion_nea']: data_variacion_nea,
        context_keys['data_variacion_nacion']: data_variacion_nacion,
        context_keys['data_variacion_ipc_table']: data_variacion_ipc_table,
        context_keys['final_chart_data']: final_chart_data,
        'meses': meses,
    }
        
    return render(request, template, context)
