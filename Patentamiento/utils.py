
from Patentamiento.models import Indicadores
from django.shortcuts import render
from Mes.models import *

from django.http import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from collections import defaultdict
from django.db.models import OuterRef, Subquery, QuerySet



class VehiculoDataProcessor:

    # Constantes de configuración
    DEFAULT_YEAR = 7
    DEFAULT_VALUE = 1
   

    @staticmethod
    def get_data_variaciones(**kwargs) -> dict:
    
        return Indicadores.objects.select_related('mes', 'anio', 'valor', 'tipoPrecio').values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'variacion_interanual',
            'variacion_intermensual',
            'total'
        ).filter(**kwargs)
    
    @classmethod
    def get_filtered_data(cls, tipo_vehiculo:int, tipo_movimiento:int, params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Args:
            tipo_vehiculo(1: moto, 2: auto)
            tipo_movimiento (1: patentamiento, 2: transferencia)
            params: Parámetros de filtrado procesados
            
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
            return cls.get_data_variaciones(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                movimiento_vehicular_id=tipo_movimiento,
                tipo_vehiculo_id = tipo_vehiculo,
                valor_id=params['valor']
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_data_variaciones(
                anio_id=cls.DEFAULT_YEAR,
                movimiento_vehicular_id=tipo_movimiento,
                tipo_vehiculo_id = tipo_vehiculo,
                valor_id=cls.DEFAULT_VALUE
            )
        

    @classmethod
    def procces_request_parameters(cls, request: HttpRequest,) -> Dict[str,any]:
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')
            valor = request.GET.get('valor')
            
            if anio_inicio and anio_fin and anio_inicio < anio_fin and valor:     
                return {
                    'anio_inicio': int(anio_inicio),
                    'anio_fin': int(anio_fin),
                    'valor':int(valor),
                    'is_valid' : True,
                    'error_message': None
                }
            else:
                return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'valor':None,
                    'is_valid' : False,
                    'error_message': 'filtros invalidos, intente nuevamente'
                }

        except ValueError:
             return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'valor':None,
                    'is_valid' : False,
                    'error_message': 'Los filtros ingresados no son validos'
                }
        
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, list]:
        """
        Procesa los datos para generar información de gráficos.
        
        Args:
            data_variacion: QuerySet con datos de variaciones
            
        Returns:
            Dict con datos organizados por año para gráficos
        """
        chart_totales = defaultdict(list)
        
        for item in data_variacion:
            anio = item['anio__anio']
            venta_total = item['total']
            if venta_total is not None:
                chart_totales[anio].append(venta_total)
        
        return dict(chart_totales)
    


def process_vehiculo_data(request:HttpRequest, tipo_vehiculo: int, tipo_movimiento: int, context_keys: Dict[str, str], template: str) -> HttpResponse:
    
    processor = VehiculoDataProcessor
    
    meses = Mes.objects.all()

    params = processor.procces_request_parameters(request)
   
    
    data_variacion = processor.get_filtered_data(tipo_vehiculo, tipo_movimiento, params)
  
    if params['is_valid']:
        type_graphic = 1
        chart_totales = processor.process_chart_data_totales(data_variacion)
    else:
        type_graphic = 0
        chart_totales = {}

    # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['chart_totales']: chart_totales,
        context_keys['type_graphic']: type_graphic,
        'meses': meses,
    }
    
    return render(request, template, context)