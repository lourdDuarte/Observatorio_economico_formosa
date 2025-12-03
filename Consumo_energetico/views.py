from django.shortcuts import render
from .utils import *
from django.shortcuts import render, redirect
from Descripcion.models import Descripcion
# Create your views here.

class RefsaViewConfig:

    # Configuración de contexto común
    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        'context_chart_formosa': 'context_chart_formosa',
        'diccionario_variacion': 'diccionario_variacion'
    }

    # Tipos de tarifa
    COMERCIAL = 1
    INDUSTRIAL = 2
    RESIDENCIAL = 3
    # Templates
    TEMPLATE_REFSA_COMERCIAL = 'Energetico/usuarios_comercial.html'
    TEMPLATE_REFSA_INDUSTRIAL = 'Energetico/usuarios_industrial.html'
    TEMPLATE_REFSA_RESIDENCIAL = 'Energetico/usuarios_residencial.html'
    TEMPLATE_DEMANDA_USUARIOS = 'Energetico/demanda_usuarios.html'

# Create your views here.
def view_refsa_comercial(request):
    
    descripcion = Descripcion.objects.filter(
          nombre_modelo = 'Consumo energetico - Tarifa comercial').values('descripcion').first()

    return process_energia_data(request, 
                                  tarifa=RefsaViewConfig.COMERCIAL,
                                  context_keys=RefsaViewConfig.CONTEXT_KEYS, 
                                  descripcion_modelo = descripcion,
                                  template=RefsaViewConfig.TEMPLATE_REFSA_COMERCIAL)

def view_refsa_industrial(request):
    
    descripcion = Descripcion.objects.filter(
          nombre_modelo = 'Consumo energetico - Tarifa industrial').values('descripcion').first()

    return process_energia_data(request, 
                                  tarifa=RefsaViewConfig.INDUSTRIAL,
                                  context_keys=RefsaViewConfig.CONTEXT_KEYS, 
                                  descripcion_modelo = descripcion,
                                  template=RefsaViewConfig.TEMPLATE_REFSA_INDUSTRIAL)

def view_refsa_residencial(request):
    
    descripcion = Descripcion.objects.filter(
          nombre_modelo = 'Consumo energetico - Tarifa residencial').values('descripcion').first()

    return process_energia_data(request, 
                                  tarifa=RefsaViewConfig.RESIDENCIAL,
                                  context_keys=RefsaViewConfig.CONTEXT_KEYS, 
                                  descripcion_modelo = descripcion,
                                  template=RefsaViewConfig.TEMPLATE_REFSA_RESIDENCIAL)


def view_demanda_usuarios(request):
    
    descripcion = Descripcion.objects.filter(
          nombre_modelo = 'Consumo energetico - Tarifa residencial').values('descripcion').first()

    return process_energia_data(request, 
                                  tarifa=RefsaViewConfig.RESIDENCIAL,
                                  context_keys=RefsaViewConfig.CONTEXT_KEYS, 
                                  descripcion_modelo = descripcion,
                                  template=RefsaViewConfig.TEMPLATE_DEMANDA_USUARIOS)


