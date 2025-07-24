

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .utils import process_contruccion_salario_data, process_contruccion_puestos_data


class ConstruccionViewConfig:
    """Configuración para las vistas de precios."""
    
    # Configuración de contexto 
    CONTEXT_KEYS_SALARIO= {
        'data_variacion': 'data_variacion',
        'salario_promedio_diccionario': 'salario_promedio_diccionario',
        'data_chart_formosa': 'data_chart_formosa',
        'data_chart_nacional': 'data_chart_nacional'
       
        
    }

     # Configuración de contexto 
    CONTEXT_KEYS_PUESTOS= {
        'data_variacion': 'data_variacion',
        'diccionario_variacion':'diccionario_variacion',
        'data_chart_formosa': 'data_chart_formosa',
        'data_chart_nacional': 'data_chart_nacional'
       
        
    }
    
    # Tipos
    TYPE_PUESTO_TRABAJO = 1
    TYPE_SALARIO = 2

    VALUE_SALARIO = 'total_empresas'
    VALUE_PUESTOS = 'total_puesto_trabajo'
    
    # Templates
    TEMPLATE_PUESTOS = 'Construccion/puestos.html'
    TEMPLATE_SALARIOS = 'Construccion/salario.html'



def view_construccion_salarios(request: HttpRequest) -> HttpResponse:
    """
    Vista para mostrar datos de sector construccion -> salarios y cantidades empresas.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Respuesta renderizada con datos 
    """
    return process_contruccion_salario_data(
        request=request,
        value_totales=ConstruccionViewConfig.VALUE_SALARIO,
        context_keys= ConstruccionViewConfig.CONTEXT_KEYS_SALARIO,
        template=ConstruccionViewConfig.TEMPLATE_SALARIOS
    )


def view_construccion_puestos(request: HttpRequest) -> HttpResponse:
    """
    Vista para mostrar datos de sector construccion -> salarios y cantidades empresas.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Respuesta renderizada con datos 
    """
    return process_contruccion_puestos_data(
        request=request,
        tipo_dato = ConstruccionViewConfig.TYPE_PUESTO_TRABAJO,
        value_totales=ConstruccionViewConfig.VALUE_PUESTOS,
        context_keys= ConstruccionViewConfig.CONTEXT_KEYS_PUESTOS,
        template=ConstruccionViewConfig.TEMPLATE_PUESTOS
    )