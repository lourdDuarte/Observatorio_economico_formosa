from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from Descripcion.models import Descripcion
# Create your views here.
from .utils import process_dgr_data
from django.shortcuts import render, redirect


class VehiculoViewConfig:



    # Configuración de contexto común
    CONTEXT_KEYS = {
        'data_recaudacion': 'data_recaudacion',
        'diccionario_recaudacion': 'diccionario_recaudacion'
    }


    
   

    
    # Templates
    TEMPLATE_RECAUDACION = 'Atp/recaudacion.html'
  



# Create your views here.
def view_recaudacion(request):
    

    descripcion = Descripcion.objects.filter(
        nombre_modelo ='ATP - Recaudacion').values('descripcion').first()
    return process_dgr_data(request,   
                            context_keys=VehiculoViewConfig.CONTEXT_KEYS, 
                            descripcion_modelo = descripcion,
                            template=VehiculoViewConfig.TEMPLATE_RECAUDACION)



