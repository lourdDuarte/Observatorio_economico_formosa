from django.shortcuts import render
from .utils import process_ipc_data
from Descripcion.models import Descripcion
# Create your views here.


class IpcViewConfig:

    CONTEXT_KEYS = {
        
            'data_variacion':'data_variacion',
            'diccionario_variacion': 'diccionario_variacion',
            
    
    }

    TEMPLATE = 'Ipc/ipc.html'

def ipc(request):
    descripcion = Descripcion.objects.filter(
        nombre_modelo='IPC'
    ).first()

    return process_ipc_data(request, 
                            context_keys=IpcViewConfig.CONTEXT_KEYS, 
                            descripcion_modelo = descripcion,
                            template=IpcViewConfig.TEMPLATE)
   