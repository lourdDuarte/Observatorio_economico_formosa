
from Ipc.models import Indicadores
from django.shortcuts import render
from Mes.models import *
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from Anio.views import *
from collections import defaultdict
from django.db.models import OuterRef, Subquery, QuerySet

def get_data_variaciones(**kwargs) -> dict:
    

    
    return Indicadores.objects.select_related('mes', 'anio', 'valor').values(
        'mes__mes',
        'mes',
        'anio__anio',
        'valor__valor',
        'variacion_interanual',
        'variacion_intermensual',
      
    ).filter(**kwargs)



def process_and_validate_ipc_data(data):
        meses_vistos = set()  # Almacena pares (mes, año)

        print("\n--- Validación de Meses Repetidos en data_variacion_ipc_table ---")
        for item_validacion in data:
            mes_nombre = item_validacion['mes__mes']
            anio = item_validacion['anio__anio']
            valor_tipo = item_validacion['valor__valor']
            
            clave_mes_anio = (mes_nombre, anio)
            
            if clave_mes_anio in meses_vistos:
                print(f"ALERTA: El mes '{mes_nombre}' del año {anio} se repite en el QuerySet. (Tipo de valor: {valor_tipo})")
            else:
                print(f"Mes encontrado por primera vez: '{mes_nombre}' del año {anio} (Tipo de valor: {valor_tipo})")
                meses_vistos.add(clave_mes_anio)
        print("--- Fin Validación de Meses Repetidos ---\n")


        grouped_data = defaultdict(lambda: {'NEA': None, 'Nacional': None, 'mes_nombre': None, 'anio': None})

        for item in data:
            mes_id = item['mes']
            mes_nombre = item['mes__mes']
            anio = item['anio__anio']
            valor_tipo = item['valor__valor'] 
            variacion = item['variacion_intermensual']

            clave = (anio, mes_id)

            grouped_data[clave]['mes_nombre'] = mes_nombre
            grouped_data[clave]['anio'] = anio

            if valor_tipo == 'NEA':
                grouped_data[clave]['NEA'] = variacion
            elif valor_tipo == 'Nacional':
                grouped_data[clave]['Nacional'] = variacion

        # Armamos la lista final, ordenando por año y mes
        final_chart_data = []

        for clave in sorted(grouped_data.keys()):  # Ordena por (año, mes_id)
            entry = grouped_data[clave]
            if entry['NEA'] is not None and entry['Nacional'] is not None:
                final_chart_data.append({
                    'mes': f"{entry['mes_nombre']} {entry['anio']}",
                    'variacion_nea': float(entry['NEA']),
                    'variacion_nacional': float(entry['Nacional'])
                })

        return final_chart_data


def data_model_ipc(request, context_keys, template):
    anio_inicio = request.GET.get('anio_inicio')
    anio_fin = request.GET.get('anio_fin')
   
    
    meses = Mes.objects.all()
   
   
    data_variacion_nea = []
    data_variacion_nacion = []
    data_variacion_ipc_table = []
    final_chart_data = []
   
    error_message = None
    
    
   
    anio_default = 7
    valor_default_nea = 3
    valor_default_nacion = 2

    
    
    if anio_inicio and anio_fin:
        try:
            anio_inicio = int(anio_inicio)
            anio_fin = int(anio_fin)
            

           
         
            data_variacion_nea = get_data_variaciones(anio_id__gte=anio_inicio,
                anio_id__lte=anio_fin,
                valor_id=valor_default_nea).order_by('anio__anio', 'mes__id')
            
            data_variacion_nacion = get_data_variaciones(anio_id__gte=anio_inicio,
                anio_id__lte=anio_fin,
                valor_id=valor_default_nacion).order_by('anio__anio', 'mes__id')
            
            data_variacion_ipc_table = data_variacion_nea | data_variacion_nacion

            final_chart_data = process_and_validate_ipc_data(data_variacion_ipc_table)

        except ValueError:
            error_message = "Los filtros ingresados no son válidos."
            data_variacion_nea = get_data_variaciones().none()
            data_variacion_nacion = get_data_variaciones().none()
    else:
        data_variacion_nea = get_data_variaciones(
                anio_id=anio_default,
                valor_id=valor_default_nea).order_by('anio__anio', 'mes__id')
            
        data_variacion_nacion = get_data_variaciones(
                anio_id=anio_default,
                valor_id=valor_default_nacion).order_by('anio__anio', 'mes__id')

        data_variacion_ipc_table = data_variacion_nea | data_variacion_nacion


       
        final_chart_data = process_and_validate_ipc_data(data_variacion_ipc_table)

    

      


       
    context = {
        'error_message': error_message,
        context_keys['data_variacion_nea']: data_variacion_nea,
        context_keys['data_variacion_nacion']: data_variacion_nacion,
        context_keys['data_variacion_ipc_table']: data_variacion_ipc_table,
        context_keys['final_chart_data']: final_chart_data,
 
        
        'meses': meses,
    }

    return render(request, template, context)
