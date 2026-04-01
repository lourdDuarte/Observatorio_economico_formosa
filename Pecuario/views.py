from django.shortcuts import render
from .utils import process_faena_data, process_stock_data, process_consumo_data, process_bovinos_data, process_porcinos_data, process_aves_data
from Descripcion.models import Descripcion


class PorcinosViewConfig:
    TEMPLATE = 'Pecuario/porcinos.html'


class BovinosViewConfig:
    TEMPLATE = 'Pecuario/bovinos.html'


class AvesViewConfig:
    TEMPLATE = 'Pecuario/aves.html'


class FaenaPecuariaViewConfig:
    TEMPLATE = 'Pecuario/faena.html'


class StockPecuarioViewConfig:
    TEMPLATE = 'Pecuario/stock.html'


class ConsumoPecuarioViewConfig:
    TEMPLATE = 'Pecuario/consumo.html'


def view_porcinos(request):
    descripcion = Descripcion.objects.filter(nombre_modelo='Porcinos- Pecuario').first()
    return process_porcinos_data(
        request,
        descripcion_modelo=descripcion,
        template=PorcinosViewConfig.TEMPLATE,
    )


def view_bovinos(request):
    descripcion = Descripcion.objects.filter(nombre_modelo='Bovinos- Pecuario').first()
    return process_bovinos_data(
        request,
        descripcion_modelo=descripcion,
        template=BovinosViewConfig.TEMPLATE,
    )

def view_aves(request):
    descripcion = Descripcion.objects.filter(nombre_modelo='Aves- Pecuario').first()
    return process_aves_data(
        request,
        descripcion_modelo=descripcion,
        template=AvesViewConfig.TEMPLATE,
    )



def view_consumo_pecuario(request):
    descripcion = Descripcion.objects.filter(nombre_modelo='Consumo Pecuario').first()
    return process_consumo_data(
        request,
        descripcion_modelo=descripcion,
        template=ConsumoPecuarioViewConfig.TEMPLATE,
    )
