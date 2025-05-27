# my_app/views.py
from django.http import JsonResponse, Http404
from django.apps import apps # Importa apps para obtener modelos dinámicamente
from django.db.models import ObjectDoesNotExist # Importar para manejar errores de objeto no encontrado

# Importa tus modelos específicos si los vas a usar directamente para mapeo
# from .models import Supermercado, OtroModelo, ModeloDeDatosX 
# O puedes listarlos si necesitas un control estricto de qué modelos son accesibles
ACCESSIBLE_MODELS = {
    'supermercado': 'Supermercado.Variacion' # 'app_label.ModelName'

    # Agrega todos los modelos que quieras hacer accesibles por esta API
}


def get_api_chart_view(request, model_name: str, anio_id: int, valor_id: int):
    # Validar y obtener el modelo dinámicamente
    model_path = ACCESSIBLE_MODELS.get(model_name.lower())
 
    model = apps.get_model(model_path)
    
    # Extraer kwargs de los query parameters de la URL
    # Por ejemplo, si la URL es /api/chart/supermercado/7/1/?tipoPrecio__id=2&otro_param=abc
    kwargs = {}
    for key, value in request.GET.items():
        # Aquí puedes añadir validaciones adicionales si es necesario
        kwargs[key] = value

    interanual = []
    intermensual = []
    meses = []

    filter_params = {
        'anio__id': anio_id,
        'valor__id': valor_id,
        **kwargs # Se incluyen los kwargs dinámicos
    }

    try:
        consult = model.objects.filter(**filter_params).order_by('mes__id') # Ordenar para ECharts
        print(consult)
        
        # Validar si la consulta devuelve algo
        if not consult.exists():
            return JsonResponse({"error": "No se encontraron datos para los parámetros proporcionados."}, status=404)

        for item in consult:
            # Asegúrate de que estos campos existen en el modelo dinámico
            # y que item.mes.mes es el atributo string del mes (ej. 'Enero')
            intermensual.append(float(item.variacion_intermensual)) # Convertir a float
            interanual.append(float(item.variacion_interanual))     # Convertir a float
            meses.append(str(item.mes.mes)) # Asegurar que es string y manejar el caso de error de Mes no serializable

    except ObjectDoesNotExist:
        return JsonResponse({"error": "Alguno de los objetos relacionados no existe."}, status=404)
    except AttributeError as e:
        # Esto captura errores si un campo como 'variacion_intermensual' no existe en el modelo
        return JsonResponse({"error": f"Error de atributo en el modelo: {e}. Asegúrate de que los campos 'variacion_intermensual', 'variacion_interanual' y 'mes.mes' existen en el modelo '{model_name}' y son accesibles."}, status=500)
    except Exception as e:
        # Captura cualquier otro error inesperado
        return JsonResponse({"error": f"Ocurrió un error inesperado: {e}"}, status=500)

    chart = {
        'xAxis': {
            'type': 'category',
            'data': meses
        },
        'yAxis': {
            'type': 'value'
        },
        'color': [
            '#c23531',
            '#2f4554',
        ],
        'series': [
            {
                'name': 'Intermensual', # Es buena práctica dar nombres a las series
                'data': intermensual,
                'type': 'line'
            },
            {
                'name': 'Interanual', # Es buena práctica dar nombres a las series
                'data': interanual,
                'type': 'line'
            }
        ]
    }

    return JsonResponse(chart)

# Si prefieres una vista basada en clases (más común para APIs con DRF)
# from rest_framework.views import APIView
# from rest_framework.response import Response
# class ChartAPIView(APIView):
#    def get(self, request, model_name: str, anio_id: int, valor_id: int, format=None):
#        # ... la misma lógica que get_api_chart_view ...
#        return Response(chart)