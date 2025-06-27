from typing import Dict, Any, Optional
from collections import defaultdict

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import OuterRef, Subquery, QuerySet

from Transferencia.models import Transferencia, Mes


class TransferenciaDataProcessor:
    DEFAULT_YEAR = 7
    DEFAULT_VALUE = 1

    @staticmethod
    def get_variacion_data(**filters)-> QuerySet:
        return Transferencia.objects.select_related(
            'mes', 'anio', 'valor'
        ).values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'total_millones',
            'variacion_anual_nominal',
            'variacion_anual_real'
        ).filter(**filters)
    
    @classmethod
    def process_request_parameters(cls, request: HttpRequest) -> Dict[str, Any]:
         
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')
            valor = request.GET.get('valor')
            
            if anio_inicio and anio_fin and valor:
                return {
                    'anio_inicio': int(anio_inicio),
                    'anio_fin': int(anio_fin),
                    'valor': int(valor),
                    'is_valid': True,
                    'error_message': None
                }
            else:
                return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'valor': None,
                    'is_valid': False,
                    'error_message': None
                }
                
        except ValueError:
            return {
                'anio_inicio': None,
                'anio_fin': None,
                'valor': None,
                'is_valid': False,
                'error_message': "Los filtros ingresados no son válidos."
            }
    

    @classmethod
    def get_filtered_data(cls,params: Dict[str, Any]) -> QuerySet:
        if params['is_valid']:
            return cls.get_variacion_data(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                valor_id=params['valor']
            ).order_by('anio__anio', 'mes__id')
        
        else:
            return cls.get_variacion_data(
                anio_id=cls.DEFAULT_YEAR,
                valor_id=cls.DEFAULT_VALUE
            )
        
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, list]:
        """
        Procesa los datos para generar información de gráficos.
        
        Args:
            data_variacion: QuerySet con datos de variaciones
            
        Returns:
            Dict con datos organizados por año para gráficos
        """
        context_chart = defaultdict(list)
        
        for item in data_variacion:
            anio = item['anio__anio']
            total = item['total_millones']
            print(total)
            if total is not None:
                context_chart[anio].append(total)
        
        return dict(context_chart)
    

def process_transferencia_data(request: HttpRequest, context_keys: Dict[str, str], template: str) -> HttpResponse:
    """
    Función principal para procesar datos del transferencia.
    
    Args:
        request: Objeto HttpRequest de Django
        
        context_keys: Claves para el contexto del template
        template: Ruta del template a renderizar
        
    Returns:
        HttpResponse: Respuesta renderizada
    """
    processor = TransferenciaDataProcessor()
    
    # Obtener todos los meses
    meses = Mes.objects.all()
    
    # Procesar parámetros de la solicitud
    params = processor.process_request_parameters(request)
    
    # Obtener datos filtrados
    data_variacion = processor.get_filtered_data( params)
    
    # Determinar tipo de gráfico y procesar datos del gráfico
    if params['is_valid']:
        type_graphic = 1
        context_chart = processor.process_chart_data_totales(data_variacion)
    else:
        type_graphic = 0
        context_chart = {}
    
    # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['context_chart']: context_chart,
        context_keys['type_graphic']: type_graphic,
        'meses': meses,
    }
    
    return render(request, template, context)