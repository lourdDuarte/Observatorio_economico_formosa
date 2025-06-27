"""
Utilidades para el módulo de Supermercado.

Este módulo contiene la lógica de negocio para el procesamiento de datos
de variaciones de precios y ventas en supermercados.
"""

from typing import Dict, Any, Optional
from collections import defaultdict

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import OuterRef, Subquery, QuerySet

from Supermercado.models import Variacion, Total, Mes

from observatorioeconomico.utils import process_data_consult


class SupermercadoDataProcessor:
    """
    Procesador de datos para el módulo de Supermercado.
    
    Maneja la obtención y procesamiento de datos de variaciones de precios
    y ventas totales.
    """
    
    # Constantes de configuración
    DEFAULT_YEAR = 7
    DEFAULT_VALUE = 1
    PRICE_TYPE_CORRIENTE = 2
    PRICE_TYPE_CONSTANTE = 1
    
    @staticmethod
    def get_variacion_data(**filters) -> QuerySet:
        """
        Obtiene datos de variaciones con información relacionada de ventas totales.
        
        Args:
            **filters: Filtros para aplicar a la consulta
            
        Returns:
            QuerySet: Consulta de variaciones con datos relacionados
        """
        venta_total_subquery = Total.objects.filter(
            anio=OuterRef('anio'),
            mes=OuterRef('mes'),
            valor=OuterRef('valor'),
            tipoPrecio=OuterRef('tipoPrecio')
        ).values('venta_total')[:1]
        
        return Variacion.objects.select_related(
            'mes', 'anio', 'valor', 'tipoPrecio'
        ).annotate(
            venta_total=Subquery(venta_total_subquery)
        ).values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'variacion_interanual',
            'variacion_intermensual',
            'venta_total'
        ).filter(**filters)
    
    @classmethod
    def process_request_parameters(cls, request: HttpRequest) -> Dict[str, Any]:
        """
        Procesa y valida los parámetros de la solicitud.
        
        Args:
            request: Objeto HttpRequest de Django
            
        Returns:
            Dict con los parámetros procesados y validados
        """
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')
            valor = request.GET.get('valor')

   

            filtros = {}
            if anio_inicio:
                filtros['anio_inicio'] = int(anio_inicio)
            if anio_fin:
                filtros['anio_fin'] = int(anio_fin)
            if valor:
                filtros['valor'] = int(valor)

           

               
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
                    'data_comparacion': []
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
    def get_filtered_data(cls, tipo_precio: int, params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Args:
            tipo_precio: Tipo de precio (1: constante, 2: corriente)
            params: Parámetros de filtrado procesados
            
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
            return cls.get_variacion_data(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                tipoPrecio_id=tipo_precio,
                valor_id=params['valor']
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_variacion_data(
                anio_id=cls.DEFAULT_YEAR,
                tipoPrecio_id=tipo_precio,
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
            venta_total = item['venta_total']
            if venta_total is not None:
                context_chart[anio].append(venta_total)
        
        return dict(context_chart)


def process_supermercado_data(request: HttpRequest, tipo_precio: int, 
                            context_keys: Dict[str, str], template: str) -> HttpResponse:
    """
    Función principal para procesar datos del supermercado.
    
    Args:
        request: Objeto HttpRequest de Django
        tipo_precio: Tipo de precio (1: constante, 2: corriente)
        context_keys: Claves para el contexto del template
        template: Ruta del template a renderizar
        
    Returns:
        HttpResponse: Respuesta renderizada
    """
    processor = SupermercadoDataProcessor()
    
    # Obtener todos los meses
    meses = Mes.objects.all()
    
    # Procesar parámetros de la solicitud
    params = processor.process_request_parameters(request)
    
    # Obtener datos filtrados
    data_variacion = processor.get_filtered_data(tipo_precio, params)
    
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