from django.shortcuts import render
from .utils import *
# Create your views here.
def ipc(request):
    context_keys = {
       
        'data_variacion_nea':'data_variacion_nea',
        'data_variacion_nacion': 'data_variacion_nacion',
        'data_variacion_ipc_table': 'data_variacion_ipc_table',
        'final_chart_data':  'final_chart_data'
 
    }

    return data_model_ipc(request, context_keys=context_keys, template='Ipc/ipc.html')
   