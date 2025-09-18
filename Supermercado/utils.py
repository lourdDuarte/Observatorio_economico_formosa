"""
Utilidades para el módulo de Supermercado.

Este módulo contiene la lógica de negocio para el procesamiento de datos
de variaciones de precios y ventas en supermercados.
"""

from typing import Dict, Any, Optional
from collections import defaultdict
import json
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import OuterRef, Subquery, QuerySet

from Supermercado.models import Variacion, Total, Mes




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
            valor = OuterRef('valor'),
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
              
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_variacion_data(
                anio_id=cls.DEFAULT_YEAR,
                tipoPrecio_id=tipo_precio,
                
            ).order_by('anio__anio', 'mes__id')
    
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, list]:
        context_chart_formosa = defaultdict(list)
        context_chart_nacional = defaultdict(list)

        for item in data_variacion:
            anio = item['anio__anio']
            venta_total = item['venta_total'] or 0  # Reemplaza None por 0

            if item['valor__valor'] == 'Formosa':
                context_chart_formosa[anio].append(venta_total)
            elif item['valor__valor'] == 'Nacional':
                context_chart_nacional[anio].append(venta_total)

        return {
            'Formosa': dict(context_chart_formosa),
            'Nacional': dict(context_chart_nacional)
        }

def diccionario(queryset):
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
    diccionario_variacion = diccionario(data_variacion)
    
    # Determinar tipo de gráfico y procesar datos del gráfico
    
    context_chart = processor.process_chart_data_totales(data_variacion)
    
    # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: diccionario_variacion,
        'data_chart_formosa': json.dumps(context_chart['Formosa']),
        'data_chart_nacional': json.dumps(context_chart['Nacional']),
       
        'meses': meses,
    }
    
    return render(request, template, context)