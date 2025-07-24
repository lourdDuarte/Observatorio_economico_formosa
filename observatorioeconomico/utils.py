# my_app/views.py
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.apps import apps # Importa apps para obtener modelos dinámicamente
from django.db.models import ObjectDoesNotExist # Importar para manejar errores de objeto no encontrado
import json

from Patentamiento.utils import VehiculoDataProcessor
from Supermercado.utils import SupermercadoDataProcessor
from Ipc.utils import IpcProcessor
from Sector_construccion.utils import ConstruccionProcessor
from sector_privado.utils import PrivadoDataProcessor

def consulta(dato, anio_inicio, anio_fin):
     
     indicadores = []
     
     if dato == 'Patentamiento - auto':
            indicadores = VehiculoDataProcessor.get_data_variaciones().filter(
                   movimiento_vehicular_id= 1,                                          
                   tipo_vehiculo_id = 2,
                   anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Transferencia - auto':
            indicadores = VehiculoDataProcessor.get_data_variaciones().filter(
                   movimiento_vehicular_id= 2,                                          
                   tipo_vehiculo_id = 2,
                   anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Patentamiento - moto':
            indicadores = VehiculoDataProcessor.get_data_variaciones().filter(
                   movimiento_vehicular_id= 1,                                          
                   tipo_vehiculo_id = 1,
                   anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Transferencia - moto':
            indicadores = VehiculoDataProcessor.get_data_variaciones().filter(
                   movimiento_vehicular_id= 2,                                          
                   tipo_vehiculo_id = 1,
                   anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Supermercado - corriente':
            indicadores = SupermercadoDataProcessor.get_variacion_data().filter(tipoPrecio_id = 2,
                   anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Supermercado - constante':
            indicadores = SupermercadoDataProcessor.get_variacion_data().filter(tipoPrecio_id = 1,
                   anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Indice precio al consumidor':
            indicadores = IpcProcessor.get_data_variaciones().filter(
                   anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Puestos trabajo - sector construccion':
            indicadores = ConstruccionProcessor.get_data_model_indicadores().filter(
                   tipo_dato = 1,anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     elif dato == 'Privado - evolucion de empleo':
            indicadores = PrivadoDataProcessor.get_variacion_data(anio_id__gte = anio_inicio,anio_id__lte= anio_fin).order_by('anio__anio', 'mes__id')
     
     return indicadores

def process_data_consult(request):

    anio_inicio = request.GET.get('anio_inicio')  # correcta
    anio_fin = request.GET.get('anio_fin')        # también
    modelo_uno = request.GET.get('modelo_uno')
    modelo_dos = request.GET.get('modelo_dos')


    indicador_uno = consulta(modelo_uno, anio_inicio, anio_fin)
    indicador_dos = consulta(modelo_dos, anio_inicio, anio_fin)

    def construir_dict(indicador, nombre_modelo):
        datos = {
            f"{nombre_modelo} Formosa intermensual": [],
            f"{nombre_modelo} Formosa interanual": [],
            f"{nombre_modelo} Nacional intermensual": [],
            f"{nombre_modelo} Nacional interanual": [],
        }
        categorias = []

        for fila in indicador:
            mes = fila['mes__mes']
            if mes not in categorias:
                categorias.append(mes)

            lugar = fila['valor__valor']
            intermensual = float(fila['variacion_intermensual'])
            interanual = float(fila['variacion_interanual'])

            datos[f"{nombre_modelo} {lugar} intermensual"].append(intermensual)
            datos[f"{nombre_modelo} {lugar} interanual"].append(interanual)

        datos['categorias'] = categorias
        return datos

    data_uno = construir_dict(indicador_uno, modelo_uno)
    
    data_dos = construir_dict(indicador_dos, modelo_dos)
    
     
  

    return render(request, 'cruce-variables.html', {
        'serie_uno': json.dumps(data_uno),
        'serie_dos': json.dumps(data_dos),
    })
    
     
     
     
 

    
    




