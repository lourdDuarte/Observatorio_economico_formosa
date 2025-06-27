from django.shortcuts import render
from .utils import process_transferencia_data
from django.http import HttpRequest, HttpResponse
# Create your views here.


class TransferenciaViewConfig:

    CONTEXT_KEYS = {
        'data_variacion': 'data_variacion',
        'type_graphic': 'type_graphic',
        'context_chart': 'context_chart'
    }

    #template
    TEMPLATE = 'Transferencias/transferencia.html'


def view_transferencia(request: HttpRequest) -> HttpResponse:
    return process_transferencia_data(
        request=request,
        context_keys=TransferenciaViewConfig.CONTEXT_KEYS,
        template = TransferenciaViewConfig.TEMPLATE
    )