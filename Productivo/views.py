from django.shortcuts import render
from .utils import process_productivo_data
from Descripcion.models import Descripcion


class ProductivoViewConfig:

    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        'diccionario_variacion': 'diccionario_variacion'
    }

    TEMPLATE = 'Productivo/productivo.html'


def view_productivo(request, tipo_cultivo):

 
    if tipo_cultivo == 1:
        descripcion = Descripcion.objects.filter(
            nombre_modelo='Productivo - Maiz'
        ).first()
    if tipo_cultivo == 2:
        descripcion = Descripcion.objects.filter(
            nombre_modelo='Productivo - Sorgo'
        ).first()
    if tipo_cultivo == 3:
        descripcion = Descripcion.objects.filter(
            nombre_modelo='Productivo - Soja'
        ).first()
    if tipo_cultivo == 4:
        descripcion = Descripcion.objects.filter(
            nombre_modelo='Productivo - Trigo'
        ).first()
    return process_productivo_data(
        request,
        tipo_cultivo=tipo_cultivo,
        context_keys=ProductivoViewConfig.CONTEXT_KEYS,
        descripcion_modelo=descripcion,
        template=ProductivoViewConfig.TEMPLATE
    )