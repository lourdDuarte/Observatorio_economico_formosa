
from Supermercado.models import *
from django.shortcuts import render
def get_data_variaciones():
    
    return Variacion.objects.select_related('mes','anio','valor' ).values(
        'mes__mes',
        'anio__anio',
        'valor__valor',
        'variacion_interanual',
        'variacion_intermensual')



def data_model_supermercado(request, tipo_precio, context_keys, template):
    anio_inicio = request.GET.get('anio_inicio')
    anio_fin = request.GET.get('anio_fin')
    valor = request.GET.get('valor') 

    meses = Mes.objects.all()
    variacion = get_data_variaciones()

    data_variacion = []
    error_message = None

    anio_default = 6
    valor_default = 1

    if anio_inicio and anio_fin and valor:
        try:
            anio_inicio = int(anio_inicio)
            anio_fin = int(anio_fin)
            valor = int(valor)

            data_variacion = variacion.filter(
                anio_id__gte=anio_inicio,
                anio_id__lte=anio_fin,
                tipoPrecio_id=tipo_precio,
                valor_id=valor
            )
            print(data_variacion)
        except ValueError:
            error_message = "Los filtros ingresados no son válidos."
            data_variacion = variacion.none()
    else:
        data_variacion = variacion.filter(
            anio_id=anio_default,
            tipoPrecio_id=tipo_precio,
            valor_id=valor_default
        )

       

    context = {
        'error_message': error_message,
        context_keys['data_variacion']: data_variacion,
        'meses': meses,
    }

    return render(request, template, context)
