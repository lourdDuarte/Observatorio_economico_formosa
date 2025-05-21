
from Supermercado.models import *
from django.shortcuts import render

from Anio.views import *
from collections import defaultdict
from django.db.models import OuterRef, Subquery, QuerySet

def get_data_variaciones():
    
    venta_total_subquery = Total.objects.filter(
    anio=OuterRef('anio'),
    mes=OuterRef('mes'),
    valor=OuterRef('valor'),
    tipoPrecio=OuterRef('tipoPrecio')
    ).values('venta_total')[:1]  # Solo el primero si hay varios

    
    return Variacion.objects.select_related('mes', 'anio', 'valor', 'tipoPrecio').annotate(
        venta_total=Subquery(venta_total_subquery)
    ).values(
        'mes__mes',
        'anio__anio',
        'valor__valor',
        'variacion_interanual',
        'variacion_intermensual',
        'venta_total'
    )



def data_model_supermercado(request, tipo_precio, context_keys, template):
    anio_inicio = request.GET.get('anio_inicio')
    anio_fin = request.GET.get('anio_fin')
    valor = request.GET.get('valor') 
    indicador_comparativo = request.GET.get('indicador')
    valor_comparativo = request.GET.get('valor-comparativo')
    meses = Mes.objects.all()
   
   
    data_variacion = []
    type_graphic = 0
    error_message = None
    context_chart = {}
    inicio = ''
    fin = ''

    anio_default = 7
    
    valor_default = 1

    if anio_inicio and anio_fin and valor:
        try:
            anio_inicio = int(anio_inicio)
            anio_fin = int(anio_fin)
            valor = int(valor)
            anios = all_year()
            for x in anios:
                if x.id == anio_inicio:
                    inicio = x.anio
                if x.id == anio_fin:
                    fin = x.anio
                

            anio_filter = str(inicio) + "-" + str(fin)
            print(anio_filter)
            data_variacion = get_data_variaciones().filter(
                anio_id__gte=anio_inicio,
                anio_id__lte=anio_fin,
                tipoPrecio_id=tipo_precio,
                valor_id=valor
            ).order_by('anio__anio', 'mes__id')
           
            # Agrupar por año
            context_chart = defaultdict(list)

            for item in data_variacion:
                anio = item['anio__anio']
                valor = item['venta_total']
                context_chart[anio].append(valor)

            # Convertir a dict normal (opcional)
            context_chart = dict(context_chart)
           
            type_graphic = 1

          
        except ValueError:
            error_message = "Los filtros ingresados no son válidos."
            data_variacion = get_data_variaciones().none()
    else:
        data_variacion = context_chart = get_data_variaciones().filter(
            anio_id=anio_default,
            tipoPrecio_id=tipo_precio,
            valor_id=valor_default
        )

       

    context = {
        'error_message': error_message,
        context_keys['data_variacion']: data_variacion,
        context_keys['context_chart']: context_chart,
        context_keys['type_graphic']: type_graphic,
       
        'meses': meses,
    }

    return render(request, template, context)
