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

from sector_privado.models import IndicadoresPrivado,CantidadesPrivado, Mes



class PrivadoDataProcessor:
   
    
    # Constantes de configuración
    DEFAULT_YEAR = 7
    DEFAULT_VALUE = 1
    ESTACIONALIDAD = 2
    
    
    @staticmethod
    def get_variacion_data(**filters) -> QuerySet:
       
        cantidad_empresas_subquery = CantidadesPrivado.objects.filter(
            anio=OuterRef('anio'),
            mes=OuterRef('mes'),
            valor=OuterRef('valor'),
            estacionalidad_id = 2 
        ).values('cantidad')[:1]
        
        return IndicadoresPrivado.objects.select_related(
            'mes', 'anio', 'valor', 'estacionalidad'
        ).annotate(
            cantidad_empresas=Subquery(cantidad_empresas_subquery)
        ).values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'estacionalidad',
            'variacion_interanual',
            'variacion_intermensual',
            'diferencia_interanual',
            'diferencia_intermensual',
            'cantidad_empresas'
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
    def get_filtered_data(cls, params: Dict[str, Any]) -> QuerySet:
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
                estacionalidad = 1,
                valor_id=params['valor']
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_variacion_data(
                anio_id=cls.DEFAULT_YEAR,
                
                estacionalidad = 1,
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
            cantidad_empresas = item['cantidad_empresas']
            if cantidad_empresas is not None:
                context_chart[anio].append(cantidad_empresas)
        
        return dict(context_chart)







class RamasPrivadoDataProcessor:
    pass



def process_privado_data(request: HttpRequest, 
                            context_keys: Dict[str, str], template: str) -> HttpResponse:
   
    processor = PrivadoDataProcessor()
    
    # Obtener todos los meses
    meses = Mes.objects.all()
    
    # Procesar parámetros de la solicitud
    params = processor.process_request_parameters(request)
    
    # Obtener datos filtrados
    data_variacion = processor.get_filtered_data(params)
   
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