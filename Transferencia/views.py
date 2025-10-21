from django.shortcuts import render
from .utils import process_transferencia_data
from django.http import HttpRequest, HttpResponse
from Descripcion.models import *
# Create your views here.


class TransferenciaViewConfig:

    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        'context_chart_formosa': 'context_chart_formosa',
        'context_chart_nacional': 'context_chart_nacional',
        'diccionario_variacion': 'diccionario_variacion'
    }

    #template
    TEMPLATE = 'Transferencias/transferencia.html'


def view_transferencia(request: HttpRequest) -> HttpResponse:
    descripcion = Descripcion.objects.filter(
          nombre_modelo = 'Transferencias').values('descripcion').first()
    return process_transferencia_data(
        request=request,
        context_keys=TransferenciaViewConfig.CONTEXT_KEYS,
        descripcion_modelo = descripcion,
        template = TransferenciaViewConfig.TEMPLATE
    )