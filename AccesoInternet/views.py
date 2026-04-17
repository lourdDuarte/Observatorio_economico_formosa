from django.shortcuts import render
from .utils import process_acceso_data
from Descripcion.models import Descripcion

# Create your views here.
class AccesioViewConfig:
    CONTEXT_KEYS = {
            'data_variacion': 'data_variacion',
            'diccionario_variacion': 'diccionario_variacion',
        }
    TEMPLATE = 'Internet/acceso_internet.html'

def view_acceso_internet(request):
    descripcion = Descripcion.objects.filter(
        nombre_modelo='Acceso internet'
    ).first()
    return process_acceso_data(
        request,
        context_keys=AccesioViewConfig.CONTEXT_KEYS,
        descripcion_modelo=descripcion,
        template=AccesioViewConfig.TEMPLATE,
    )