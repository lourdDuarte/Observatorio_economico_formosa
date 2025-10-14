
from Patentamiento.models import Indicadores
from django.shortcuts import render
from Mes.models import *
import json
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any
from collections import defaultdict
from django.db.models import QuerySet



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
               
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_data_variaciones(
                anio_id=cls.DEFAULT_YEAR,
                movimiento_vehicular_id=tipo_movimiento,
                tipo_vehiculo_id = tipo_vehiculo,
                
            ).order_by('anio__anio', 'mes__id')
    
    @classmethod
    def procces_request_parameters(cls, request: HttpRequest,) -> Dict[str,any]:
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
    
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, list]:
        context_chart_formosa = defaultdict(list)
        context_chart_nacional = defaultdict(list)

        for item in data_variacion:
            anio = item['anio__anio']
            venta_total = item['total'] or 0  # Reemplaza None por 0

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

def process_vehiculo_data(request:HttpRequest, tipo_vehiculo: int, tipo_movimiento: int, context_keys: Dict[str, str], template: str) -> HttpResponse:
    
    processor = VehiculoDataProcessor
    
    meses = Mes.objects.all()

    params = processor.procces_request_parameters(request)
   
    
    data_variacion = processor.get_filtered_data(tipo_vehiculo, tipo_movimiento, params)
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















