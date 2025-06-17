from django.shortcuts import render
from .utils import process_ipc_data
# Create your views here.


class IpcViewConfig:

    CONTEXT_KEYS = {
        
            'data_variacion_nea':'data_variacion_nea',
            'data_variacion_nacion': 'data_variacion_nacion',
            'data_variacion_ipc_table': 'data_variacion_ipc_table',
            'final_chart_data':  'final_chart_data'
    
    }

    TEMPLATE = 'Ipc/ipc.html'

def ipc(request):

    return process_ipc_data(request, 
                            context_keys=IpcViewConfig.CONTEXT_KEYS, 
                            template=IpcViewConfig.TEMPLATE)
   