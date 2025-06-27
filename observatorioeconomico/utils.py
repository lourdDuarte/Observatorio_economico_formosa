# my_app/views.py
from django.http import JsonResponse, Http404
from django.apps import apps # Importa apps para obtener modelos dinámicamente
from django.db.models import ObjectDoesNotExist # Importar para manejar errores de objeto no encontrado

from Patentamiento.utils import *


from Patentamiento.utils import VehiculoDataProcessor





def process_data_consult(type_date,params: Dict[str, Any]) -> QuerySet:
    
    
     if type_date == 'Patentamiento - auto':
            print(VehiculoDataProcessor.get_data_variaciones(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                tipo_vehiculo_id = 1,
                valor_id=params['valor_modelo']))
     
     else:
        pass
    #  elif type_date == 'Transferencia - auto':
    #         indicadores = VehiculoDataProcessor.get_data_variaciones()
    #         consult = indicadores.filter(anio_id=año, valor_id=value, movimiento_vehicular_id=2, tipo_vehiculo_id=2)
    #  elif type_date == 'Patentamiento - moto':
    #         indicadores = VehiculoDataProcessor.get_data_variaciones()
    #         consult = indicadores.filter(anio_id=año, valor_id=value, movimiento_vehicular_id=1, tipo_vehiculo_id=1)
    #  elif type_date == 'Transferencia - moto':
    #         indicadores = VehiculoDataProcessor.get_data_variaciones()
    #         consult = indicadores.filter(anio_id=año, valor_id=value, movimiento_vehicular_id=2, tipo_vehiculo_id=1)
    #  elif type_date == 'Supermercado - corriente':
    #         indicadores = SupermercadoDataProcessor.get_variacion_data()
    #         consult = indicadores.filter(anio_id=año, valor_id=value, tipoPrecio_id=2)
    #  elif type_date == 'Supermercado - constante':
    #         indicadores = SupermercadoDataProcessor.get_variacion_data()
    #         consult = indicadores.filter(anio_id=año, valor_id=value, tipoPrecio_id=1)
    #  elif type_date == 'Indice precio al consumidor':
    #         indicadores = IpcProcessor.get_data_variaciones()
    #         consult = indicadores.filter(anio_id=año, valor_id=value)
     
     
 

    
    




