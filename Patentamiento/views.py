from django.shortcuts import render

# Create your views here.
from .utils import process_vehiculo_data
from django.shortcuts import render, redirect


class VehiculoViewConfig:



    # Configuración de contexto común
    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        
        'context_chart_formosa': 'context_chart_formosa',
        'context_chart_nacional': 'context_chart_nacional',
        'diccionario_variacion': 'diccionario_variacion'
    }


    
    # Tipos de movimientos vehiculares
    PATENTAMIENTO = 1
    TRANSFERENCIA = 2

    # Tipos de vehiculos
    MOTO = 1
    AUTO = 2


    
    # Templates
    TEMPLATE_AUTO_PATENTAMIENTO = 'Auto/patentamiento.html'
    TEMPLATE_AUTO_TRANSFERENCIA= 'Auto/transferencia.html'

    TEMPLATE_MOTO_PATENTAMIENTO = 'Moto/Patentamiento.html'
    TEMPLATE_MOTO_TRANSFERENCIA= 'Moto/Transferencia.html'



# Create your views here.
def view_patentamiento_auto(request):
    


    return process_vehiculo_data(request, 
                                  tipo_vehiculo=VehiculoViewConfig.AUTO,
                                  tipo_movimiento= VehiculoViewConfig.PATENTAMIENTO, 
                                  context_keys=VehiculoViewConfig.CONTEXT_KEYS, 
                                  template=VehiculoViewConfig.TEMPLATE_AUTO_PATENTAMIENTO)


def view_patentamiento_moto(request):
    
     return  process_vehiculo_data(request, 
                                  tipo_vehiculo=VehiculoViewConfig.MOTO,
                                  tipo_movimiento= VehiculoViewConfig.PATENTAMIENTO, 
                                  context_keys=VehiculoViewConfig.CONTEXT_KEYS, 
                                  template=VehiculoViewConfig.TEMPLATE_MOTO_PATENTAMIENTO)
    
def view_transferencia_auto(request):
    
     return  process_vehiculo_data(request, 
                                  tipo_vehiculo=VehiculoViewConfig.AUTO,
                                  tipo_movimiento= VehiculoViewConfig.TRANSFERENCIA, 
                                  context_keys=VehiculoViewConfig.CONTEXT_KEYS, 
                                  template=VehiculoViewConfig.TEMPLATE_AUTO_TRANSFERENCIA)
    


def view_transferencia_moto(request):
    
     return  process_vehiculo_data(request, 
                                  tipo_vehiculo=VehiculoViewConfig.MOTO,
                                  tipo_movimiento= VehiculoViewConfig.TRANSFERENCIA, 
                                  context_keys=VehiculoViewConfig.CONTEXT_KEYS, 
                                  template=VehiculoViewConfig.TEMPLATE_MOTO_TRANSFERENCIA)
    




