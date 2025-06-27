

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .utils import process_construccion_data


class ConstruccionViewConfig:
    """Configuración para las vistas de precios."""
    
    # Configuración de contexto 
    CONTEXT_KEYS= {
        'final_chart_data': 'final_chart_data',
        'data_variacion_salario_table':'data_variacion_salario_table',
        'type_graphic': 'type_graphic',
        'chart_totales': 'chart_totales',
        'salario_formosa':'salario_formosa'
        
    }
    
    # Tipos
    TYPE_PUESTO_TRABAJO = 1
    TYPE_SALARIO = 2
    
    # Templates
    TEMPLATE_PUESTOS = 'Construccion/puestos.html'
    TEMPLATE_SALARIOS = 'Construccion/salario.html'


# def view_construccion_puestos(request: HttpRequest) -> HttpResponse:
#     """
#     Vista para mostrar datos de sector construccion -> variaciones y total de puestos.
    
#     Args:
#         request: Objeto HttpRequest de Django
        
#     Returns:
#         HttpResponse: Respuesta renderizada con datos 
#     """
#     return process_construccion_data(
#         request=request,
#         tipo_dato=ConstruccionViewConfig.TYPE_PUESTO_TRABAJO,
#         context_keys=ConstruccionViewConfig.CONTEXT_KEYS,
#         template=ConstruccionViewConfig.TEMPLATE_PUESTOS
#     )


def view_construccion_salarios(request: HttpRequest) -> HttpResponse:
    """
    Vista para mostrar datos de sector construccion -> salarios y cantidades empresas.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Respuesta renderizada con datos 
    """
    return process_construccion_data(
        request=request,
        
        context_keys= ConstruccionViewConfig.CONTEXT_KEYS,
        template=ConstruccionViewConfig.TEMPLATE_SALARIOS
    )