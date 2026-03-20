from Productivo.models import (
    IndicadoresPrecioCultivo,
    ProduccionCampaniaCultivo,
    ParticipacionProdFormosa,
    CampaniaCultivo,
)
from django.shortcuts import render
from Mes.models import Mes
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from django.db.models import QuerySet, Count
from Anio.models import Anio


class BaseDataProcessor:
    """
    Clase base con lógica de validación de parámetros GET reutilizable.

    Las subclases deben definir PARAM_INICIO y PARAM_FIN con los nombres
    de los parámetros esperados en la query string.
    """

    PARAM_INICIO: str = ''
    PARAM_FIN: str = ''

    @classmethod
    def process_request_parameters(cls, request: HttpRequest) -> Dict[str, Any]:
        """
        Procesa y valida los parámetros de rango de la solicitud GET.

        Returns:
            Dict con las claves del rango, 'is_valid' y 'error_message'.
        """
        try:
            inicio = request.GET.get(cls.PARAM_INICIO)
            fin = request.GET.get(cls.PARAM_FIN)

            if not inicio and not fin:
                return {
                    cls.PARAM_INICIO: None,
                    cls.PARAM_FIN: None,
                    'is_valid': False,
                    'error_message': None,
                }

            filtros = {}
            if inicio:
                filtros[cls.PARAM_INICIO] = int(inicio)
            if fin:
                filtros[cls.PARAM_FIN] = int(fin)

            if cls.PARAM_INICIO in filtros and cls.PARAM_FIN in filtros:
                if filtros[cls.PARAM_FIN] < filtros[cls.PARAM_INICIO]:
                    return {
                        **filtros,
                        'is_valid': False,
                        'error_message': "Los filtros aplicados son incorrectos: el valor de fin no puede ser menor que el de inicio.",
                    }
                return {**filtros, 'is_valid': True, 'error_message': None}

            return {
                **filtros,
                'is_valid': False,
                'error_message': "Debe seleccionar ambos valores para aplicar el filtro.",
            }

        except ValueError:
            return {
                cls.PARAM_INICIO: None,
                cls.PARAM_FIN: None,
                'is_valid': False,
                'error_message': "Los filtros ingresados no son válidos.",
            }


class ProductivoDataProcessor(BaseDataProcessor):
    """
    Procesador de datos de comercialización (precios y variaciones por cultivo).
    """

    PARAM_INICIO = 'anio_inicio'
    PARAM_FIN = 'anio_fin'

    @staticmethod
    def get_data_variaciones(**kwargs) -> QuerySet:
        return IndicadoresPrecioCultivo.objects.select_related(
            'mes', 'anio', 'tipo_cultivo'
        ).values(
            'mes__mes',
            'anio__anio',
            'tipo_cultivo__tipo_cultivo',
            'precio_nacional',
            'precio_internacional',
            'variacion_mensual',
            'variacion_fob',
        ).filter(**kwargs)

    @classmethod
    def get_default_year(cls) -> Optional[int]:
        """
        Retorna el ID del año más reciente que tenga datos de todos los cultivos.
        """
        total_cultivos = IndicadoresPrecioCultivo.objects.values(
            'tipo_cultivo'
        ).distinct().count()

        resultado = (
            IndicadoresPrecioCultivo.objects
            .values('anio_id')
            .annotate(cant_cultivos=Count('tipo_cultivo', distinct=True))
            .filter(cant_cultivos=total_cultivos)
            .order_by('-anio_id')
            .first()
        )
        return resultado['anio_id'] if resultado else None

    @classmethod
    def get_filtered_data(cls, params: Dict[str, Any]) -> QuerySet:
        if params['is_valid']:
            return cls.get_data_variaciones(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            ).order_by('anio__anio', 'mes__id')

        return cls.get_data_variaciones(
            anio_id=cls.get_default_year(),
        ).order_by('anio__anio', 'mes__id')

    @staticmethod
    def build_chart_data(queryset) -> Dict[str, Any]:
        """
        Transforma el queryset de variaciones en estructura para gráficos.

        Evalúa el queryset una sola vez para evitar queries redundantes.

        Returns:
            Dict con clave 'meses' y series '<cultivo> Mensual' / '<cultivo> FOB'.
        """
        items = list(queryset)
        meses = []
        data = {}

        for item in items:
            label = f"{item['mes__mes']} {item['anio__anio']}"
            if label not in meses:
                meses.append(label)

        for item in items:
            cultivo = item['tipo_cultivo__tipo_cultivo']
            if cultivo not in data:
                data[cultivo] = {
                    'mensual': {m: 0 for m in meses},
                    'fob': {m: 0 for m in meses},
                }

        for item in items:
            label = f"{item['mes__mes']} {item['anio__anio']}"
            cultivo = item['tipo_cultivo__tipo_cultivo']
            data[cultivo]['mensual'][label] = float(item['variacion_mensual'])
            data[cultivo]['fob'][label] = float(item['variacion_fob'])

        resultado = {'meses': meses}
        for cultivo, valores in data.items():
            resultado[f'{cultivo} Mensual'] = [valores['mensual'][m] for m in meses]
            resultado[f'{cultivo} FOB'] = [valores['fob'][m] for m in meses]

        return resultado


class ProduccionDataProcessor(BaseDataProcessor):
    """
    Procesador de datos de producción agrícola por campaña y cultivo.
    """

    PARAM_INICIO = 'campania_inicio'
    PARAM_FIN = 'campania_fin'

    @staticmethod
    def get_data_produccion(**kwargs) -> QuerySet:
        return ProduccionCampaniaCultivo.objects.select_related(
            'campania', 'valor', 'tipo_cultivo'
        ).values(
            'campania__campania',
            'valor__valor',
            'tipo_cultivo__tipo_cultivo',
            'superficie_sembrada',
            'superficie_cosechada',
            'produccion',
        ).filter(**kwargs)

    @staticmethod
    def get_data_participacion(**kwargs) -> QuerySet:
        return ParticipacionProdFormosa.objects.select_related(
            'campania', 'tipo_cultivo'
        ).values(
            'campania__campania',
            'tipo_cultivo__tipo_cultivo',
            'participacion',
        ).filter(**kwargs)

    @classmethod
    def get_filtered_data(cls, params: Dict[str, Any]) -> Dict[str, QuerySet]:
        if params['is_valid']:
            produccion = cls.get_data_produccion(
                campania_id__gte=params['campania_inicio'],
                campania_id__lte=params['campania_fin'],
            ).order_by('campania__id')
            participacion = cls.get_data_participacion(
                campania_id__gte=params['campania_inicio'],
                campania_id__lte=params['campania_fin'],
            ).order_by('campania__id')
        else:
            produccion = cls.get_data_produccion().order_by('campania__id')
            participacion = cls.get_data_participacion().order_by('campania__id')

        return {'produccion': produccion, 'participacion': participacion}

    @staticmethod
    def build_chart_data(queryset) -> Dict[str, Any]:
        """
        Transforma el queryset de participaciones en estructura para gráficos.

        Returns:
            Dict con clave 'meses' (campañas) y series 'Participacion en <cultivo>'.
        """
        items = sorted(queryset, key=lambda x: x['campania__campania'])
        campanias = []
        data = {}

        for item in items:
            campania = item['campania__campania']
            if campania not in campanias:
                campanias.append(campania)

        for item in items:
            cultivo = item['tipo_cultivo__tipo_cultivo']
            if cultivo not in data:
                data[cultivo] = {c: 0 for c in campanias}

        for item in items:
            data[item['tipo_cultivo__tipo_cultivo']][item['campania__campania']] = float(item['participacion'])

        resultado = {'meses': campanias}
        for cultivo, valores in data.items():
            resultado[f'Participacion en {cultivo}'] = [valores[c] for c in campanias]

        return resultado


def process_comercializacion_data(
    request: HttpRequest,
    context_keys: Dict[str, str],
    descripcion_modelo: str,
    template: str,
) -> HttpResponse:
    params = ProductivoDataProcessor.process_request_parameters(request)
    data_variacion = ProductivoDataProcessor.get_filtered_data(params)
    diccionario_variacion = ProductivoDataProcessor.build_chart_data(data_variacion)

    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: diccionario_variacion,
        'descripcion_modelo': descripcion_modelo,
        'meses': Mes.objects.all(),
        'anios': Anio.objects.all().order_by('anio'),
    }
    return render(request, template, context)


def process_produccion_data(
    request: HttpRequest,
    descripcion_modelo: str,
    context_keys: Dict[str, str],
    template: str,
) -> HttpResponse:
    params = ProduccionDataProcessor.process_request_parameters(request)
    data = ProduccionDataProcessor.get_filtered_data(params)
    diccionario_variacion = ProduccionDataProcessor.build_chart_data(data['participacion'])

    context = {
        'error_message': params['error_message'],
        context_keys['produccion']: data['produccion'],
        context_keys['diccionario_variacion']: diccionario_variacion,
        'descripcion_modelo': descripcion_modelo,
        'campanias': CampaniaCultivo.objects.all().order_by('campania'),
    }
    return render(request, template, context)
