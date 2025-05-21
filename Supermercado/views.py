from .utils import *
from django.shortcuts import render, redirect

# Create your views here.
def view_precio_corriente(request):
    
    context_keys = {
       
        'data_variacion': 'data_variacion',
        'type_graphic': 'type_graphic',
        'context_chart': 'context_chart'
 
    }

    return data_model_supermercado(request, tipo_precio=2, context_keys=context_keys, template='Supermercado/precio-corriente.html')
    


def view_precio_constante(request):
    
    context_keys = {
       
        'data_variacion': 'data_variacion',
        'type_graphic': 'type_graphic',
        'context_chart': 'context_chart'
 
    }

    return data_model_supermercado(request, tipo_precio=1, context_keys=context_keys, template='Supermercado/precio-constante.html')
    