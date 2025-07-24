from django.shortcuts import render
from .utils import process_transferencia_data
from django.http import HttpRequest, HttpResponse
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
    return process_transferencia_data(
        request=request,
        context_keys=TransferenciaViewConfig.CONTEXT_KEYS,
        template = TransferenciaViewConfig.TEMPLATE
    )