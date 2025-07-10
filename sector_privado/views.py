from django.shortcuts import render

# Create your views here.
"""
Vistas para el módulo de Supermercado.

Este módulo contiene las vistas que manejan las solicitudes HTTP
para las diferentes funcionalidades del supermercado.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .utils import process_privado_data


class PrivadoViewConfig:
    """Configuración para las vistas de precios."""
    
    # Configuración de contexto común
    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        'type_graphic': 'type_graphic',
        'context_chart': 'context_chart',
    }
    
   
    
    # Templates
    TEMPLATE_PRIVADO = 'Sector_privado/privado.html'
    


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

