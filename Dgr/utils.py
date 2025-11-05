from Dgr.models import Recaudacion
from django.shortcuts import render
from Mes.models import *
import json
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from collections import defaultdict
from django.db.models import  QuerySet


class DgrDataProcessor:
    DEFAULT_YEAR = 7

  

    @staticmethod
    def get_data_recaudacion(**kwargs) -> QuerySet:
        """
        Obtiene los datos de recaudación desde la base de datos según los filtros proporcionados.
        Args:
            **kwargs: Filtros opcionales para la consulta (por ejemplo, anio_id, tipo_id, etc.).
        Returns:
            QuerySet: Conjunto de resultados con los campos seleccionados:
                - mes__mes
                - anio__anio
                - valor__valor
                - tipo__tipo
                - recaudacion
        """
        return Recaudacion.objects.select_related('mes', 'anio', 'valor', 'tipo').values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'tipo__tipo',
            'recaudacion'
        ).filter(**kwargs)

    @classmethod
    def get_filtered_data(cls, params: Dict[str, Any]) -> QuerySet:
        """
        Aplica filtros a la consulta de recaudación según los parámetros proporcionados.
        Args:
            params (dict): Diccionario con los parámetros de filtrado. 
                Debe contener al menos:
                    - is_valid (bool): Indica si los parámetros ingresados son válidos.
                    - anio_inicio (int): Año inicial del rango (si is_valid es True).
                    - anio_fin (int): Año final del rango (si is_valid es True).
        Returns:
            QuerySet: Conjunto de resultados de la tabla Recaudacion filtrado y ordenado.
                      Si los parámetros no son válidos, devuelve los datos del año por defecto.
        """
        if params['is_valid']:
            return cls.get_data_recaudacion(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                tipo_id__in=[1, 3]
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_data_recaudacion(
                anio_id=cls.DEFAULT_YEAR,
                tipo_id__in=[1, 3]
            ).order_by('anio__anio', 'mes__id')

      
    @classmethod
    def procces_request_parameters(cls, request: HttpRequest,) -> Dict[str,any]:
        """
        Procesa y valida los parámetros de año enviados mediante la solicitud HTTP (GET).

        Este método toma los parámetros 'anio_inicio' y 'anio_fin' del request,
        los valida y devuelve un diccionario con el estado de la validación,
        los valores convertidos a enteros (si son válidos) y mensajes de error en caso necesario.
        Args:
            request (HttpRequest): Objeto de solicitud HTTP que contiene los parámetros GET.
        Returns:
            dict: Diccionario con las siguientes claves:
                - anio_inicio (int | None): Año inicial del rango o None si no fue proporcionado.
                - anio_fin (int | None): Año final del rango o None si no fue proporcionado.
                - is_valid (bool): Indica si los parámetros son válidos.
                - error_message (str | None): Mensaje de error en caso de validación fallida.
            
            Casos posibles:
                - Si no se enviaron filtros: devuelve `is_valid=False` y `error_message=None`.
                - Si el año final < año inicial: devuelve `is_valid=False` con mensaje de error.
                - Si falta uno de los dos años: devuelve `is_valid=False` con mensaje de error.
                - Si ambos años son válidos: devuelve `is_valid=True` sin errores.
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
                    'error_message': None  #No mostrar error al ingresar por primera vez
                }
            if anio_inicio:
                filtros['anio_inicio'] = int(anio_inicio)
            if anio_fin:
                filtros['anio_fin'] = int(anio_fin)
            if 'anio_inicio' in filtros and 'anio_fin' in filtros:
                if filtros['anio_fin'] < filtros['anio_inicio']:
                    return {
                        **filtros,
                        'is_valid': False,
                        'error_message': (
                            "Los filtros aplicados son incorrectos: "
                            "el año de fin no puede ser menor que el de inicio."
                        )
                    }
                else:
                    return {
                        **filtros,
                        'is_valid': True,
                        'error_message': None
                    }
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



def diccionario(queryset):
    """
    Adapta una queryset de datos de recaudación al formato de diccionario esperado por el template.
    La función procesa una queryset proveniente del modelo `Recaudacion`, separa los valores según
    el tipo de recaudación ("Tributaria" e "IIBB") y genera un diccionario con listas paralelas de meses
    y valores de recaudación, ajustadas al mismo tamaño para visualización en un grafico
    Args:
        queryset (QuerySet | list[dict]): 
            Queryset o lista de diccionarios resultante de una consulta con los campos:
            - 'mes__mes' (str): Nombre del mes.
            - 'anio__anio' (int): Año correspondiente.
            - 'tipo__tipo' (str): Tipo de recaudación ('Tributaria' o 'IIBB').
            - 'recaudacion' (float | int): Valor de recaudación.
    Returns:
        dict: Diccionario adaptado con las siguientes claves:
            - **meses** (list[str]): Lista de meses comunes a ambas recaudaciones.
            - **Valor recaudacion Tributaria** (list[float]): Valores de recaudación tributaria.
            - **Valor recaudacion IIBB** (list[float]): Valores de recaudación IIBB.
    """
    recaudacion = []
    recaudacion_tributaria = []
    recaudacion_iibb = []
    
    meses = []

    meses_tributaria = []
    meses_iibb = []

    for item in queryset:
        mes = item['mes__mes'] + " " +  str(item['anio__anio'])
        tipo = item['tipo__tipo']
        recaudacion = (item['recaudacion'])
       

        if tipo == 'Tributaria':
            recaudacion_tributaria.append(recaudacion)
            meses_tributaria.append(mes)
            
        elif tipo == 'IIBB':
            recaudacion_iibb.append(recaudacion)
            
            meses_iibb.append(mes)

    # Obtener la cantidad mínima común
    minimo = min(len(recaudacion_tributaria), len(recaudacion_iibb))

    # Recortar todas las listas al mismo tamaño
    datos = {
        'meses': meses_tributaria[:minimo],  
        'Valor recaudacion Tributaria': recaudacion_tributaria[:minimo],
        'Valor recaudacion IIBB': recaudacion_iibb[:minimo],
        
    }

    return datos


def process_dgr_data(request:HttpRequest, 
                     context_keys: Dict[str, str], 
                     descripcion_modelo:str, 
                     template: str) -> HttpResponse:
    """
    Procesa los datos de recaudación (DGR) y renderiza la plantilla HTML con los resultados.

    Esta función integra el flujo completo:
    - Obtiene los parámetros de filtrado desde la solicitud HTTP.
    - Ejecuta la consulta correspondiente en el modelo de recaudación.
    - Adapta los resultados en formato de diccionario.
    - Construye el contexto final para renderizar en la plantilla HTML.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP que contiene los parámetros GET.
        context_keys (Dict[str, str]): Diccionario con las claves utilizadas para el contexto.
            - **data_recaudacion**: clave para acceder al queryset filtrado.
            - **diccionario_recaudacion**: clave para acceder al queryset adaptado como diccionario.
        descripcion_modelo (str): Descripción del modelo que se visualizará en el HTML.
        template (str): Nombre o ruta de la plantilla HTML que se renderizará.

    Returns:
        HttpResponse: Respuesta HTTP renderizada con el contexto generado, que incluye:
            - **error_message**: mensaje de error si la validación de filtros falla.
            - **data_recaudacion**: queryset con los datos filtrados.
            - **diccionario_recaudacion**: datos adaptados en formato de diccionario.
            - **descripcion_modelo**: descripción textual del modelo consultado.
            - **meses**: listado de meses cargado desde la base de datos.
    """
    processor = DgrDataProcessor

    meses = Mes.objects.all()
    params = processor.procces_request_parameters(request)

    data_recaudacion = processor.get_filtered_data(params)

    diccionario_recaudacion = diccionario(data_recaudacion)

     # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_recaudacion']: data_recaudacion,
        context_keys['diccionario_recaudacion']: diccionario_recaudacion,
        'descripcion_modelo' : descripcion_modelo,
        'meses': meses,
    }
    
    return render(request, template, context)