from typing import Dict, Any, Optional
from collections import defaultdict
import json
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
    def get_filtered_data(cls,params: Dict[str, Any]) -> QuerySet:
        if params['is_valid']:
            return cls.get_variacion_data(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
               
            ).order_by('anio__anio', 'mes__id')
        
        else:
            return cls.get_variacion_data(
                anio_id=cls.DEFAULT_YEAR,
               
            )
        
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, list]:
        context_chart_formosa = defaultdict(list)
        context_chart_nacional = defaultdict(list)

        for item in data_variacion:
            anio = item['anio__anio']
            total = item['total_millones'] or 0  # Reemplaza None por 0

            if item['valor__valor'] == 'Formosa':
                context_chart_formosa[anio].append(total)
            elif item['valor__valor'] == 'Nacional':
                context_chart_nacional[anio].append(total)

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
        intermensual = float(item['variacion_anual_real'])
        interanual = float(item['variacion_anual_nominal'])

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
        'Variacion real Formosa': formosa_intermensual[:minimo],
        'Variacion nominal Formosa': formosa_interanual[:minimo],
        'Variacion real Nacional': nacional_intermensual[:minimo],
        'Variacion nominal Nacional': nacional_interanual[:minimo],
    }

    return datos
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