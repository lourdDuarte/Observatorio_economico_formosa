
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
    def get_filtered_data(cls,  params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
            return cls.get_data_variaciones(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin']).order_by('anio__anio', 'mes__id')
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
                    
                    'is_valid' : False,
                    'error_message': 'Los filtros ingresados no son validos'
                }
        
    
def diccionario(queryset):
    nea_intermensual = []
    nea_interanual = []
    nacional_intermensual = []
    nacional_interanual = []
    meses = []

    # Para mantener el orden, usamos listas separadas para cada región con su mes
    meses_nea = []
    meses_nacional = []

    for item in queryset:
        mes = item['mes__mes'] + " " +  str(item['anio__anio'])
        region = item['valor__valor']
        intermensual = float(item['variacion_intermensual'])
        interanual = float(item['variacion_interanual'])

        if region == 'NEA':
            nea_intermensual.append(intermensual)
            nea_interanual.append(interanual)
            meses_nea.append(mes)
        elif region == 'Nacional':
            nacional_intermensual.append(intermensual)
            nacional_interanual.append(interanual)
            meses_nacional.append(mes)

    # Obtener la cantidad mínima común
    minimo = min(len(nea_intermensual), len(nacional_intermensual))
   
    # Recortar todas las listas al mismo tamaño
    datos = {
        'meses': meses_nea[:minimo],  # o meses_nacional[:minimo], ambos deberían coincidir en orden
        'Valor intermensual NEA': nea_intermensual[:minimo],
        'Valor interanual NEA': nea_interanual[:minimo],
        'Valor intermensual Nacional': nacional_intermensual[:minimo],
        'Valor interanual Nacional': nacional_interanual[:minimo],
    }

    return datos

def process_ipc_data(request:HttpRequest, context_keys: Dict[str, str], template: str) -> HttpResponse:

    meses = Mes.objects.all()

    processor = IpcProcessor
    params = processor.procces_request_parameters(request)


    data_variacion = processor.get_filtered_data(params)
    diccionario_variacion = diccionario(data_variacion)
   

       
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: diccionario_variacion,
        'meses': meses,
    }
        
    return render(request, template, context)
