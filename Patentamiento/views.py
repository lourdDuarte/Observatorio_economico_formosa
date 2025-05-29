from django.shortcuts import render

# Create your views here.
from .utils import *
from django.shortcuts import render, redirect

# Create your views here.
def view_patentamiento_auto(request):
    
    context_keys = {
       
        'data_variacion': 'data_variacion',
       
      
        'type_graphic': 'type_graphic',
        'context_chart': 'context_chart'
 
    }

    return data_model_vehiculo(request, tipo_vehiculo=2,tipo_movimiento= 1, context_keys=context_keys, template='Auto/patentamiento.html')
    
def view_transferencia_auto(request):
    
    context_keys = {
       
        'data_variacion': 'data_variacion',
       
      
        'type_graphic': 'type_graphic',
        'context_chart': 'context_chart'
 
    }

    return data_model_vehiculo(request, tipo_vehiculo=2,tipo_movimiento= 2, context_keys=context_keys, template='Auto/transferencia.html')
    




