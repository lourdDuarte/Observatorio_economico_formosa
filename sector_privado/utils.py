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

from sector_privado.models import IndicadoresPrivado,CantidadesPrivado,AsalariadoRama, Mes



class PrivadoDataProcessor:
   
    
    # Constantes de configuración
    DEFAULT_YEAR = 7
    
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

            filtros = {}

            # Si no se aplicaron filtros, devolver estado predeterminado (sin errores)
            if not anio_inicio and not anio_fin:
                return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'is_valid': False,
                    'error_message': None  # No mostrar error al ingresar por primera vez
                }

            # Procesar y validar filtros cuando existen
            if anio_inicio:
                filtros['anio_inicio'] = int(anio_inicio)
            if anio_fin:
                filtros['anio_fin'] = int(anio_fin)

            # Validar que el año fin no sea menor que el año inicio
            if 'anio_inicio' in filtros and 'anio_fin' in filtros:
                if filtros['anio_fin'] < filtros['anio_inicio']:
                    return {
                        **filtros,
                        'is_valid': False,
                        'error_message': "Los filtros aplicados son incorrectos: el año de fin no puede ser menor que el de inicio."
                    }
                else:
                    return {
                        **filtros,
                        'is_valid': True,
                        'error_message': None
                    }

            # Si falta alguno de los filtros (solo inicio o solo fin)
            return {
                **filtros,
                'is_valid': False,
                'error_message': "Debe seleccionar ambos años para aplicar el filtro."
            }

        except ValueError:
            return {
                'anio_inicio': None,
                'anio_fin': None,
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
                estacionalidad = 2,
                
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_variacion_data(
                anio_id=cls.DEFAULT_YEAR,
                
                estacionalidad = 2,
                
            ).order_by('anio__anio', 'mes__id')
    
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, list]:
        context_chart_formosa = defaultdict(list)
        context_chart_nacional = defaultdict(list)

        for item in data_variacion:
            anio = item['anio__anio']
            cantidad_empresas = item['cantidad_empresas'] or 0  # Reemplaza None por 0

            if item['valor__valor'] == 'Formosa':
                context_chart_formosa[anio].append(cantidad_empresas)
            elif item['valor__valor'] == 'Nacional':
                context_chart_nacional[anio].append(cantidad_empresas)

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


def process_privado_data(request: HttpRequest, 
                            context_keys: Dict[str, str], template: str) -> HttpResponse:
   
    processor = PrivadoDataProcessor()
    
    # Obtener todos los meses
    meses = Mes.objects.all()
    
    # Procesar parámetros de la solicitud
    params = processor.process_request_parameters(request)
    
    # Obtener datos filtrados
    data_variacion = processor.get_filtered_data(params)
    diccionario_variacion = diccionario(data_variacion)
    
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





class PrivadoRamasDataProcessor:

    DEFAULT_YEAR = 6

    @staticmethod
    def get_cantidad_asalariados(**filters) -> QuerySet:
        return AsalariadoRama.objects.select_related(
            'rama', 'trimestre', 'anio', 'mes'
        ).values(
            'rama__rama',
            'trimestre__trimestre',
            'mes__mes',
            'anio__anio',
            'valor',
            'cantidad'
        ).filter(**filters)
    

    @classmethod
    def process_request_parameters(cls, request: HttpRequest) -> Dict[str, Any]:
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')
            trimestre_inicio = request.GET.get('trimestre_inicio')
            trimestre_fin = request.GET.get('trimestre_fin')      
   

            filtros = {}
            if anio_inicio:
                filtros['anio_inicio'] = int(anio_inicio)
            if anio_fin:
                filtros['anio_fin'] = int(anio_fin)
            if trimestre_inicio:
                filtros['trimestre_inicio'] = int(trimestre_inicio)
            if trimestre_fin:
                filtros['trimestre_fin'] = int(trimestre_fin)

           

               
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
                'trimestre_inicio': None,
                'trimestre_fin': None,
                'is_valid': False,
                'error_message': "Los filtros ingresados no son válidos."
            }
        
    @classmethod
    def get_filtered_data_cantidades(cls, params: Dict[str, Any]) -> QuerySet:
        if params['is_valid']:
            return cls.get_cantidad_asalariados(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                trimestre_id__gte=params['trimestre_inicio'],
                trimestre_id__lte=params['trimestre_fin'],    
            ).order_by('anio__anio', 'mes__id')
        else:
             return cls.get_cantidad_asalariados(
                anio_id=cls.DEFAULT_YEAR,
            
            )
        

    @staticmethod
    def process_chart_ramas_cantidad(data_cantidades: QuerySet) -> Dict[str, Dict[str, Dict[str, int]]]:
        context_chart = defaultdict(lambda: defaultdict(dict))
        # Resultado: context_chart[rama][anio][trimestre] = cantidad

        for item in data_cantidades:
            trimestre = item['trimestre__trimestre']
            anio = str(item['anio__anio'])
            cantidad = item['cantidad']
            rama = item['rama__rama']

            if cantidad is not None:
                context_chart[rama][anio][trimestre] = int(cantidad)

        return dict(context_chart)

def process_privado_ramas_data(request: HttpRequest, 
                            context_keys: Dict[str, str], template: str) -> HttpResponse:
   
    processor = PrivadoRamasDataProcessor()
    
    # Obtener todos los meses
    meses = Mes.objects.all()
    
    # Procesar parámetros de la solicitud
    params = processor.process_request_parameters(request)
    
    # Obtener datos filtrados
    data_variacion = processor.get_filtered_data_cantidades(params)
   
    # Determinar tipo de gráfico y procesar datos del gráfico
    if params['is_valid']:
        
        context_chart = processor.process_chart_ramas_cantidad(data_variacion)
        
    else:
        type_graphic = 0
        context_chart = processor.process_chart_ramas_cantidad(data_variacion)
    

    
    # Construir contexto
    context = {
        'error_message': params['error_message'],
        
        context_keys['chart_data_json']: json.dumps(context_chart),
        context_keys['data_variacion']: data_variacion,
       
        'meses': meses,
    }
    
    return render(request, template, context)
