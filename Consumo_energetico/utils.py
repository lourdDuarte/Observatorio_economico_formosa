from Consumo_energetico.models import *
from django.shortcuts import render
from Mes.models import *
import json
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any
from collections import defaultdict
from django.db.models import QuerySet

class EnergiaDataProcessor:

    
     # Constantes de configuración
    DEFAULT_YEAR = 7
    DEFAULT_VALUE = 1

    @staticmethod
    def get_data_cammesa(**kwargs) -> dict:
    
        return Cammesa.objects.select_related('mes', 'anio', 'valor', 'tarifa').values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'tarifa__tipo_tarifa',
            'demanda',
            'variacion_interanual',
            'variacion_intermensual',
            
        ).filter(**kwargs)
    
    @classmethod
    def get_filtered_data(cls, tarifa:int, params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Args:
            tipo_vehiculo(1: moto, 2: auto)
            tipo_movimiento (1: patentamiento, 2: transferencia)
            params: Parámetros de filtrado procesados
            
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
            
            return cls.get_data_cammesa(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                tarifa_id=tarifa
               
            ).order_by('anio__anio', 'mes__id')
        else:
            return cls.get_data_cammesa(
                anio_id=cls.DEFAULT_YEAR,
                tarifa_id=tarifa
                
            ).order_by('anio__anio', 'mes__id')
    
    @classmethod
    def procces_request_parameters(cls, request: HttpRequest,) -> Dict[str,any]:

        """
        Procesa y valida los parámetros de la solicitud.
        
        Args:
            request: Objeto HttpRequest de Django
            
        Returns:
            Dict con los parámetros procesados y validados
        """
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')

            filtros = {}

            # Si no se aplicaron filtros, devolver estado predeterminado (sin errores)
            if not anio_inicio and not anio_fin:
                return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'is_valid': False,
                    'error_message': None  # No mostrar error al ingresar por primera vez
                }

            # Procesar y validar filtros cuando existen
            if anio_inicio:
                filtros['anio_inicio'] = int(anio_inicio)
            if anio_fin:
                filtros['anio_fin'] = int(anio_fin)

            # Validar que el año fin no sea menor que el año inicio
            if 'anio_inicio' in filtros and 'anio_fin' in filtros:
                if filtros['anio_fin'] < filtros['anio_inicio']:
                    return {
                        **filtros,
                        'is_valid': False,
                        'error_message': "Los filtros aplicados son incorrectos: el año de fin no puede ser menor que el de inicio."
                    }
                else:
                    return {
                        **filtros,
                        'is_valid': True,
                        'error_message': None
                    }

            # Si falta alguno de los filtros (solo inicio o solo fin)
            return {
                **filtros,
                'is_valid': False,
                'error_message': "Debe seleccionar ambos años para aplicar el filtro."
            }

        except ValueError:
            return {
                'anio_inicio': None,
                'anio_fin': None,
                'is_valid': False,
                'error_message': "Los filtros ingresados no son válidos."
            }
        
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, list]:

        context_chart_formosa = defaultdict(list)
        

        for item in data_variacion:
            anio = item['anio__anio']
            venta_total = item['demanda'] or 0  # Reemplaza None por 0

            if item['valor__valor'] == 'Formosa':
                context_chart_formosa[anio].append(venta_total)
           

        return {
            'Formosa': dict(context_chart_formosa),
            
        }
    
    @staticmethod
    def procesar_filtro_anio(request: HttpRequest) -> dict:
        """
        Procesa un único filtro de año.
        Si no se aplica filtro, usa el DEFAULT_YEAR.
        Devuelve:
        - anio (int)
        - is_valid (bool)
        - error_message (str o None)
        """

        anio = request.GET.get('anio')

        # Si no eligió año → usar el año por defecto
        if not anio:
            return {
                'anio': EnergiaDataProcessor.DEFAULT_YEAR,
                'is_valid': True,   # Se toma como válido porque sí se usará un año
                'error_message': None
            }

        try:
            anio = int(anio)
            return {
                'anio': anio,
                'is_valid': True,
                'error_message': None
            }

        except ValueError:
            return {
                'anio': EnergiaDataProcessor.DEFAULT_YEAR,
                'is_valid': True,
                'error_message': "El año ingresado no es válido, se cargó el año por defecto."
            }

    @staticmethod
    def get_last_demanda_by_tarifa_year(params: dict) -> dict:
        """
        Devuelve la última demanda por tarifa dentro del año elegido.
        """

        tarifas = TipoTarifa.objects.all().order_by("id")

        series = []
        labels = []

        for tarifa in tarifas:

            qs = Cammesa.objects.filter(tarifa=tarifa)

            # Aplicar filtro por año si corresponde
            if params["is_valid"]:
                qs = qs.filter(anio_id=params["anio"])

            ultimo = qs.order_by('-mes__id').values('demanda').first()

            valor = float(ultimo['demanda']) if ultimo else 0

            series.append(valor)
            labels.append(tarifa.tipo_tarifa)

        return {
            "series": series,
            "labels": labels
        }


    @staticmethod
    def get_last_usuarios_by_tarifa_year(params: dict) -> dict:
        """
        Devuelve la última cantidad de usuarios por tarifa dentro del año elegido.
        Si el último es 0, toma el anterior dentro del mismo año.
        """

        tarifas = TipoTarifa.objects.all().order_by("id")
        resultados = {}

        for tarifa in tarifas:

            qs = Refsa.objects.filter(tarifa=tarifa)

            # Filtro por año
            if params["is_valid"]:
                qs = qs.filter(anio_id=params["anio"])

            registros = qs.order_by('-mes__id').values('cantidad_usuarios')

            valor = 0

            if registros:
                ultimo = registros[0]

                if ultimo['cantidad_usuarios'] not in ["0", 0, None, ""]:
                    valor = float(ultimo['cantidad_usuarios'])
                else:
                    if len(registros) > 1:
                        anterior = registros[1]
                        valor = float(anterior['cantidad_usuarios'])
                    else:
                        valor = 0

            resultados[tarifa.tipo_tarifa] = [valor]

        return resultados



def diccionario(queryset):
    formosa_intermensual = []
    formosa_interanual = []
   
    meses_formosa = []
   
    for item in queryset:
        mes = item['mes__mes'] + " " +  str(item['anio__anio'])
        region = item['valor__valor']
        intermensual = float(item['variacion_intermensual'])
        interanual = float(item['variacion_interanual'])

        if region == 'Formosa':
            formosa_intermensual.append(intermensual)
            formosa_interanual.append(interanual)
            meses_formosa.append(mes)
       

    # Obtener la cantidad mínima común
    minimo = min(len(formosa_intermensual), len(formosa_interanual))

    # Recortar todas las listas al mismo tamaño
    datos = {
        'meses': meses_formosa[:minimo],  # o meses_nacional[:minimo], ambos deberían coincidir en orden
        'Valor intermensual Formosa': formosa_intermensual[:minimo],
        'Valor interanual Formosa': formosa_interanual[:minimo],
        
    }

    return datos


def process_energia_data(request:HttpRequest, tarifa: int, context_keys: Dict[str, str],descripcion_modelo:str, template: str) -> HttpResponse:
    
    processor = EnergiaDataProcessor
    meses = Mes.objects.all()

    params = processor.procces_request_parameters(request)
   
    
    data_variacion = processor.get_filtered_data(tarifa, params)
    diccionario_variacion = diccionario(data_variacion)
    
    context_chart = processor.process_chart_data_totales(data_variacion)
    

    # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: diccionario_variacion,
        'data_chart_formosa': json.dumps(context_chart['Formosa']),
        'descripcion_modelo': descripcion_modelo,
        'meses': meses,
    }
    
    return render(request, template, context)

def process_energia_resumen(request: HttpRequest, descripcion_modelo: str, template: str) -> HttpResponse:

    processor = EnergiaDataProcessor

    # Nuevo filtro (1 solo año)
    params = processor.procesar_filtro_anio(request)
    print(params)
    # DEMANDA (torta)
    demanda = processor.get_last_demanda_by_tarifa_year(params)
    demanda_series = json.dumps(demanda["series"])
    demanda_labels = json.dumps(demanda["labels"])

    # USUARIOS (barras)
    usuarios = processor.get_last_usuarios_by_tarifa_year(params)
    usuarios_json = json.dumps(usuarios)

    context = {
        'error_message': params['error_message'],
        'descripcion_modelo': descripcion_modelo,

        # torta
        'demanda_series': demanda_series,
        'demanda_labels': demanda_labels,

        # barras
        'usuarios_barras': usuarios_json,
    }

    return render(request, template, context)
