from django.shortcuts import render, redirect
import requests
from requests.exceptions import RequestException, SSLError
from collections import defaultdict
import json
from Supermercado.models import Variacion as supermercado
from Patentamiento.models import Indicadores as auto


def obtener_datos_de_modelo(
    modelo_django,
    anio_id: int,
    valor_id: int,
    # Los kwargs permiten pasar filtros adicionales específicos de cada modelo
    **kwargs) -> dict:
    """
    Realiza una consulta genérica a un modelo de Django y extrae
    variacion_interanual, variacion_intermensual y fecha_actualizacion.
    """
    
    try:
        # Construye el diccionario de filtros base
        filtros = {
            'anio__id': anio_id,
            'valor__id': valor_id,
            **kwargs # Agrega los filtros específicos pasados como kwargs
        }

        obj = modelo_django.objects.filter(**filtros).order_by('-id').first()
        if obj:
           
            return {
                "valor_intermensual": getattr(obj, 'variacion_intermensual', 'N/D'),
                "valor_interanual": getattr(obj, 'variacion_interanual', 'N/D'),
                "fecha_actualizacion": getattr(obj, 'fecha_actualizacion', 'N/D'),
            }
        else:
            return {
                "valor_intermensual": "N/D",
                "valor_interanual": "N/D",
               "fecha_actualizacion": "N/D"
            }
    except:
        print("error")


def generar_panel_json(
  
) -> str:
    """
    Genera el JSON estructurado para el panel de tarjetas.
    """
    panel_data = {}

    
    panel_data["Supermercado"] = {
        "Precio Corriente": obtener_datos_de_modelo(
            modelo_django=supermercado,
            anio_id=7,
            valor_id=1,
            tipoPrecio__id=2
        ),
        "Precio Constante": obtener_datos_de_modelo(
            modelo_django=supermercado,
            anio_id=7,
            valor_id=1,
            tipoPrecio__id=1
        )
    }
    panel_data["Auto"] ={
        "Patentamiento": obtener_datos_de_modelo(
            modelo_django = auto,
            anio_id= 6,
            valor_id= 1,
            movimiento_vehicular = 1,
            tipo_vehiculo = 2
        ),
        "Transeferencia":  obtener_datos_de_modelo(
            modelo_django = auto,
            anio_id= 6,
            valor_id= 1,
            movimiento_vehicular= 2,
            tipo_vehiculo = 2
        ),
    }
    return panel_data
    
def index(request):
 
    data_json = generar_panel_json()
    context = {
        'data_json' : data_json
    }

    

    URL = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias"
    
    try:
        response = requests.get(URL, verify=False)
        response.raise_for_status()  # Lanza HTTPError si el código no es 200
        filter_api = [1,29,31,32,40,144,146]
        data_api = defaultdict(lambda: {'valor': [], 'fecha': []})
        if response.status_code == 200:
        
            data = response.json()
            for key in data['results']:
                if key['idVariable'] in filter_api:
                    descripcion = key['descripcion']
                    valor = key['valor']
                    fecha = key['fecha']
                    if key['idVariable'] == 29 or key['idVariable'] == 146 or key['idVariable'] == 144 :
                        data_api[descripcion]['valor'].append(str(valor) + '%')
                        data_api[descripcion]['fecha'].append(fecha)
                    else:
                        data_api[descripcion]['valor'].append(valor)
                        data_api[descripcion]['fecha'].append(fecha)
                        
                    
            
            data_combinada = {
                descripcion: list(zip(info['fecha'], info['valor']))
                for descripcion, info in data_api.items()
            }

            context.update({
                'data_combinada': data_combinada
            })

    except (SSLError, RequestException) as e:
        context.update ({
            'error':f"[ERROR BCRA] {e}"
        })

    
        
    return render (request, 'index.html', context)




def consulta(model, value, anio_start, anio_end):

    data = model

def cruce_variables(request):
   
    return render (request, 'cruce-variables.html')