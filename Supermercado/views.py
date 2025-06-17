"""
Vistas para el módulo de Supermercado.

Este módulo contiene las vistas que manejan las solicitudes HTTP
para las diferentes funcionalidades del supermercado.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .utils import process_supermercado_data


class PriceViewConfig:
    """Configuración para las vistas de precios."""
    
    # Configuración de contexto común
    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        'type_graphic': 'type_graphic',
        'context_chart': 'context_chart'
    }
    
    # Tipos de precio
    PRECIO_CONSTANTE = 1
    PRECIO_CORRIENTE = 2
    
    # Templates
    TEMPLATE_CONSTANTE = 'Supermercado/precio-constante.html'
    TEMPLATE_CORRIENTE = 'Supermercado/precio-corriente.html'


def view_precio_corriente(request: HttpRequest) -> HttpResponse:
    """
    Vista para mostrar datos de precios corrientes.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Respuesta renderizada con datos de precios corrientes
    """
    return process_supermercado_data(
        request=request,
        tipo_precio=PriceViewConfig.PRECIO_CORRIENTE,
        context_keys=PriceViewConfig.CONTEXT_KEYS,
        template=PriceViewConfig.TEMPLATE_CORRIENTE
    )


def view_precio_constante(request: HttpRequest) -> HttpResponse:
    """
    Vista para mostrar datos de precios constantes.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Respuesta renderizada con datos de precios constantes
    """
    return process_supermercado_data(
        request=request,
        tipo_precio=PriceViewConfig.PRECIO_CONSTANTE,
        context_keys=PriceViewConfig.CONTEXT_KEYS,
        template=PriceViewConfig.TEMPLATE_CONSTANTE
    )