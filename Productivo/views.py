from django.shortcuts import render
from .utils import process_produccion_data, process_comercializacion_data
from Descripcion.models import Descripcion


class ComercializacionViewConfig:

    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        'diccionario_variacion': 'diccionario_variacion',
    }
    TEMPLATE = 'Productivo/comercializacion.html'


class ProduccionViewConfig:

    CONTEXT_KEYS = {
        'produccion': 'produccion',
        'diccionario_variacion': 'diccionario_variacion',
    }
    TEMPLATE = 'Productivo/productivo.html'


def view_comercializacion(request):
    descripcion = Descripcion.objects.filter(
        nombre_modelo='Sector agricola - comercializacion'
    ).first()
    return process_comercializacion_data(
        request,
        context_keys=ComercializacionViewConfig.CONTEXT_KEYS,
        descripcion_modelo=descripcion,
        template=ComercializacionViewConfig.TEMPLATE,
    )


def view_produccion(request):
    descripcion = Descripcion.objects.filter(
        nombre_modelo='Sector agricola - produccion'
    ).first()
    return process_produccion_data(
        request,
        context_keys=ProduccionViewConfig.CONTEXT_KEYS,
        descripcion_modelo=descripcion,
        template=ProduccionViewConfig.TEMPLATE,
    )
