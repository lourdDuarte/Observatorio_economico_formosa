from .utils import *
from django.shortcuts import render, redirect

# Create your views here.
def view_precio_corriente(request):
    
    context_keys = {
       
        'data_variacion': 'data_variacion',
 
    }

    return data_model_supermercado(request, tipo_precio=2, context_keys=context_keys, template='supermercado/precio-corriente.html')
    