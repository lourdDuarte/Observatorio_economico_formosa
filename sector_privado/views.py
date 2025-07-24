from django.shortcuts import render

# Create your views here.
"""
Vistas para el módulo de Supermercado.

Este módulo contiene las vistas que manejan las solicitudes HTTP
para las diferentes funcionalidades del supermercado.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .utils import process_privado_data, process_privado_ramas_data


class PrivadoViewConfig:
    """Configuración para las vistas de precios."""
    
    # Configuración de contexto común
    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        
        'context_chart_formosa': 'context_chart_formosa',
        'context_chart_nacional': 'context_chart_nacional',
        'diccionario_variacion': 'diccionario_variacion'
    }

    CONTEXT_KEYS_RAMAS = {
       
        'chart_data_json': 'chart_data_json',
        'data_variacion': 'data_variacion',
    }
   
    
    # Templates
    TEMPLATE_PRIVADO = 'Sector_privado/privado.html'
    TEMPLATE_RAMAS = 'Sector_privado/ramas_privado.html'
    


def view_sector_privado(request: HttpRequest) -> HttpResponse:
    """
    Vista para mostrar datos de precios corrientes.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Respuesta renderizada con datos de precios corrientes
    """
    return process_privado_data(
        request=request,
        context_keys=PrivadoViewConfig.CONTEXT_KEYS,
        template=PrivadoViewConfig.TEMPLATE_PRIVADO
    )


def view_sector_privado_ramas(request):
    return process_privado_ramas_data(
        request=request,
        context_keys=PrivadoViewConfig.CONTEXT_KEYS_RAMAS,
        template=PrivadoViewConfig.TEMPLATE_RAMAS
    )

