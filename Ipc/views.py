from django.shortcuts import render
from .utils import process_ipc_data
# Create your views here.


class IpcViewConfig:

    CONTEXT_KEYS = {
        
            'data_variacion':'data_variacion',
            'diccionario_variacion': 'diccionario_variacion',
            
    
    }

    TEMPLATE = 'Ipc/ipc.html'

def ipc(request):

    return process_ipc_data(request, 
                            context_keys=IpcViewConfig.CONTEXT_KEYS, 
                            template=IpcViewConfig.TEMPLATE)
   