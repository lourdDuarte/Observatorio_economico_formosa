import json
from typing import Dict, Any, Optional
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from Anio.models import Anio

from .models import FaenaPecuario, StockPecuario, ConsumoCapita, ConsumoTotalProteina, ProdDestIndustria


class PecuarioDataProcessor:

    PARAM_INICIO = 'anio_inicio'
    PARAM_FIN = 'anio_fin'

    @classmethod
    def process_request_parameters(cls, request: HttpRequest) -> Dict[str, Any]:
        try:
            inicio = request.GET.get(cls.PARAM_INICIO)
            fin = request.GET.get(cls.PARAM_FIN)

            if not inicio and not fin:
                return {cls.PARAM_INICIO: None, cls.PARAM_FIN: None, 'is_valid': False, 'error_message': None}

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
                        'error_message': "El filtro de fin no puede ser menor que el de inicio.",
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

    @staticmethod
    def get_default_year(model) -> Optional[int]:
        result = model.objects.values('anio_id').order_by('-anio_id').first()
        return result['anio_id'] if result else None

    # ------------------------------------------------------------------ #
    # QUERIES                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_data_faena(**kwargs) -> QuerySet:
        return FaenaPecuario.objects.select_related(
            'mes', 'anio', 'valor', 'tipo_ganado'
        ).values(
            'mes__mes', 'mes__id', 'anio__anio',
            'valor__valor', 'tipo_ganado__tipo_ganado', 'cabezas',
        ).filter(**kwargs).order_by('anio__anio', 'mes__id')

    @staticmethod
    def get_data_stock(**kwargs) -> QuerySet:
        return StockPecuario.objects.select_related(
            'mes', 'anio', 'valor', 'tipo_ganado'
        ).values(
            'mes__mes', 'mes__id', 'anio__anio',
            'valor__valor', 'tipo_ganado__tipo_ganado', 'stock',
        ).filter(**kwargs).order_by('anio__anio', 'mes__id')

    @staticmethod
    def get_data_consumo_capita(**kwargs) -> QuerySet:
        return ConsumoCapita.objects.select_related(
            'mes', 'anio', 'valor', 'tipo_ganado'
        ).values(
            'mes__mes', 'mes__id', 'anio__anio',
            'valor__valor', 'tipo_ganado__tipo_ganado', 'consumo',
        ).filter(**kwargs).order_by('anio__anio', 'mes__id')

    @staticmethod
    def get_data_consumo_total(**kwargs) -> QuerySet:
        return ConsumoTotalProteina.objects.select_related(
            'mes', 'anio', 'valor'
        ).values(
            'mes__mes', 'mes__id', 'anio__anio',
            'valor__valor', 'consumo_total',
        ).filter(**kwargs).order_by('anio__anio', 'mes__id')
    
    @staticmethod
    def get_data_prod_industria(**kwargs) -> QuerySet:
        return ProdDestIndustria.objects.select_related(
            'mes', 'anio', 'valor', 'tipo_ganado'
        ).values(
            'mes__mes', 'mes__id', 'anio__anio',
            'valor__valor', 'tipo_ganado__tipo_ganado', 'produccion'
        ).filter(**kwargs).order_by('anio__anio', 'mes__id')

    # ------------------------------------------------------------------ #
    # FILTROS POR PARAMS                                                   #
    # ------------------------------------------------------------------ #

    @classmethod
    def get_filtered_prod_industria(cls, params: Dict) -> QuerySet:
        if params['is_valid']:
            return cls.get_data_prod_industria(
                tipo_ganado_id=3,
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
        default = cls.get_default_year(ProdDestIndustria)
        return cls.get_data_prod_industria(tipo_ganado_id=3, anio_id=default) if default else cls.get_data_prod_industria(tipo_ganado_id=3)
   
    @classmethod
    def get_filtered_porcinos_stock(cls, params: Dict) -> QuerySet:
        if params['is_valid']:
            return cls.get_data_stock(
                tipo_ganado_id=2,
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
        default = cls.get_default_year(StockPecuario)
        return cls.get_data_stock(tipo_ganado_id=2, anio_id=default) if default else cls.get_data_stock(tipo_ganado_id=2)

    @classmethod
    def get_filtered_porcinos_faena(cls, params: Dict) -> QuerySet:
        if params['is_valid']:
            return cls.get_data_faena(
                tipo_ganado_id=2,
                valor__valor='Nacional',
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
        result = FaenaPecuario.objects.filter(tipo_ganado_id=2, valor__valor='Nacional').values('anio_id').order_by('-anio_id').first()
        default = result['anio_id'] if result else None
        return cls.get_data_faena(tipo_ganado_id=2, valor__valor='Nacional', anio_id=default) if default else cls.get_data_faena(tipo_ganado_id=2, valor__valor='Nacional')
    
    @classmethod
    def get_filtered_aves_faena(cls, params: Dict) -> QuerySet:
        if params['is_valid']:
            return cls.get_data_faena(
                tipo_ganado_id=3,
                valor__valor='Nacional',
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
        result = FaenaPecuario.objects.filter(tipo_ganado_id=3, valor__valor='Nacional').values('anio_id').order_by('-anio_id').first()
        default = result['anio_id'] if result else None
        return cls.get_data_faena(tipo_ganado_id=3, valor__valor='Nacional', anio_id=default) if default else cls.get_data_faena(tipo_ganado_id=3, valor__valor='Nacional')
    


    @classmethod
    def get_filtered_bovinos_faena(cls, params: Dict) -> QuerySet:
        if params['is_valid']:
            return cls.get_data_faena(
                tipo_ganado_id=1,
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
        default = cls.get_default_year(FaenaPecuario)
        return cls.get_data_faena(tipo_ganado_id=1, anio_id=default) if default else cls.get_data_faena(tipo_ganado_id=1)

    @classmethod
    def get_filtered_bovinos_stock(cls, params: Dict) -> QuerySet:
        if params['is_valid']:
            return cls.get_data_stock(
                tipo_ganado_id=1,
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
        default = cls.get_default_year(StockPecuario)
        return cls.get_data_stock(tipo_ganado_id=1, anio_id=default) if default else cls.get_data_stock(tipo_ganado_id=1)

    @classmethod
    def get_filtered_consumo(cls, params: Dict) -> Dict:
        if params['is_valid']:
            capita = cls.get_data_consumo_capita(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
            total = cls.get_data_consumo_total(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            )
        else:
            default_capita = cls.get_default_year(ConsumoCapita)
            default_total = cls.get_default_year(ConsumoTotalProteina)
            capita = cls.get_data_consumo_capita(anio_id=default_capita) if default_capita else cls.get_data_consumo_capita()
            total = cls.get_data_consumo_total(anio_id=default_total) if default_total else cls.get_data_consumo_total()
        return {'capita': capita, 'total': total}

    # ------------------------------------------------------------------ #
    # BUILDERS DE CHART                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def build_chart_por_tipo(queryset, campo_valor: str) -> Dict[str, Any]:
        """
        Genera estructura para area_chart_variation.
        Eje X: 'Mes Año'. Series: '{tipo_ganado} - {valor}'.
        Las series que contienen 'Nacional' se ocultan por defecto en el JS.
        """
        items = list(queryset)
        meses = []
        series: Dict[str, Dict] = {}

        for item in items:
            label = f"{item['mes__mes']} {item['anio__anio']}"
            if label not in meses:
                meses.append(label)

        for item in items:
            clave = f"{item['tipo_ganado__tipo_ganado']}"
            if clave not in series:
                series[clave] = {m: None for m in meses}

        for item in items:
            label = f"{item['mes__mes']} {item['anio__anio']}"
            clave = f"{item['tipo_ganado__tipo_ganado']}"
            val = item[campo_valor]
            series[clave][label] = float(val) if val is not None else None

        # Solo incluir meses donde TODOS los tipos tienen dato
        meses_completos = [
            m for m in meses
            if all(series[clave].get(m) is not None for clave in series)
        ]

        resultado: Dict[str, Any] = {'meses': meses_completos}
        for clave, valores in series.items():
            resultado[clave] = [valores[m] for m in meses_completos]

        return resultado

    @staticmethod
    def build_chart_consumo_total(queryset) -> Dict[str, Any]:
        """
        Genera estructura para area_chart_variation con una sola serie.
        """
        items = list(queryset)
        meses = []
        valores = []

        for item in items:
            meses.append(f"{item['mes__mes']} {item['anio__anio']}")
            val = item['consumo_total']
            valores.append(float(val) if val is not None else None)

        return {
            'meses': meses,
            'Consumo Total Proteína': valores,
        }

def diccionario_nacional(campo: str, queryset: QuerySet, nombre_serie: str = 'Nacional') -> Dict[str, list]:
    meses = []
    valores = []
    for item in queryset:
        meses.append(f"{item['mes__mes']} {item['anio__anio']}")
        val = item[campo]
        valores.append(float(val) if val is not None else None)
    return {
        'meses': meses,
        nombre_serie: valores,
    }


def diccionario_bovinos(campo: str, queryset: QuerySet) -> Dict[str, list]:
    data = {
        'Formosa': [],
        'Nacional': [],
    }

    meses_formosa, meses_nacional = [], []

    for item in queryset:
        mes_str = f"{item['mes__mes']} {item['anio__anio']}"
        region = item['valor__valor']
        valor = float(item[campo]) if item[campo] is not None else None

        if region == 'Formosa':
            data['Formosa'].append(valor)
            meses_formosa.append(mes_str)
        elif region == 'Nacional':
            data['Nacional'].append(valor)
            meses_nacional.append(mes_str)

    minimo = min(len(data['Formosa']), len(data['Nacional']))

    data['meses'] = meses_formosa[:minimo]
    for key in list(data.keys()):
        if key != 'meses':
            data[key] = data[key][:minimo]

    return data
# ------------------------------------------------------------------ #
# FUNCIONES DE PROCESO (llamadas desde views)                         #
# ------------------------------------------------------------------ #

def process_porcinos_data(request: HttpRequest, descripcion_modelo, template: str) -> HttpResponse:
    params = PecuarioDataProcessor.process_request_parameters(request)
    qs_faena = PecuarioDataProcessor.get_filtered_porcinos_faena(params)
    qs_stock = PecuarioDataProcessor.get_filtered_porcinos_stock(params)
    chart_faena = diccionario_nacional('cabezas', qs_faena, nombre_serie='Porcinos')
    chart_stock = diccionario_bovinos('stock', qs_stock)
    anio_ids = FaenaPecuario.objects.filter(tipo_ganado_id=2).values_list('anio_id', flat=True).distinct()
    context = {
        'error_message': params['error_message'],
        'chart_faena': json.dumps(chart_faena),
        'chart_stock': json.dumps(chart_stock),
        'descripcion_modelo': descripcion_modelo,
        'anios': Anio.objects.filter(id__in=anio_ids).order_by('anio'),
    }
    return render(request, template, context)

def process_aves_data(request: HttpRequest, descripcion_modelo, template: str) -> HttpResponse:
    params = PecuarioDataProcessor.process_request_parameters(request)
    qs_faena = PecuarioDataProcessor.get_filtered_aves_faena(params)
    chart_faena = diccionario_nacional('cabezas', qs_faena, nombre_serie='Aves')
    prod_industria = PecuarioDataProcessor.get_filtered_prod_industria(params)
    anio_ids = FaenaPecuario.objects.filter(tipo_ganado_id=3).values_list('anio_id', flat=True).distinct()
    context = {
        'error_message': params['error_message'],
        'chart_faena': json.dumps(chart_faena),
        'prod_industria': prod_industria,
        'descripcion_modelo': descripcion_modelo,
        'anios': Anio.objects.filter(id__in=anio_ids).order_by('anio'),
    }
    return render(request, template, context)


def process_bovinos_data(request: HttpRequest, descripcion_modelo, template: str) -> HttpResponse:
    params = PecuarioDataProcessor.process_request_parameters(request)
    qs_faena = PecuarioDataProcessor.get_filtered_bovinos_faena(params)
    qs_stock = PecuarioDataProcessor.get_filtered_bovinos_stock(params)
    chart_faena = diccionario_bovinos('cabezas', qs_faena)
    chart_stock = diccionario_bovinos('stock', qs_stock)
    anio_ids = FaenaPecuario.objects.filter(tipo_ganado_id=1).values_list('anio_id', flat=True).distinct()
    context = {
        'error_message': params['error_message'],
        'chart_faena': json.dumps(chart_faena),
        'chart_stock': json.dumps(chart_stock),
        'descripcion_modelo': descripcion_modelo,
        'anios': Anio.objects.filter(id__in=anio_ids).order_by('anio'),
    }
    return render(request, template, context)


def process_faena_data(request: HttpRequest, descripcion_modelo, template: str) -> HttpResponse:
    params = PecuarioDataProcessor.process_request_parameters(request)
    data = PecuarioDataProcessor.get_filtered_faena(params)
    chart = PecuarioDataProcessor.build_chart_por_tipo(data, 'cabezas')
    anio_ids = FaenaPecuario.objects.values_list('anio_id', flat=True).distinct()
    context = {
        'error_message': params['error_message'],
        'data': data,
        'chart_data': json.dumps(chart),
        'descripcion_modelo': descripcion_modelo,
        'anios': Anio.objects.filter(id__in=anio_ids).order_by('anio'),
    }
    return render(request, template, context)


def process_stock_data(request: HttpRequest, descripcion_modelo, template: str) -> HttpResponse:
    params = PecuarioDataProcessor.process_request_parameters(request)
    data = PecuarioDataProcessor.get_filtered_stock(params)
    chart = PecuarioDataProcessor.build_chart_por_tipo(data, 'stock')
    anio_ids = StockPecuario.objects.values_list('anio_id', flat=True).distinct()
    context = {
        'error_message': params['error_message'],
        'data': data,
        'chart_data': json.dumps(chart),
        'descripcion_modelo': descripcion_modelo,
        'anios': Anio.objects.filter(id__in=anio_ids).order_by('anio'),
    }
    return render(request, template, context)


def process_consumo_data(request: HttpRequest, descripcion_modelo, template: str) -> HttpResponse:
    params = PecuarioDataProcessor.process_request_parameters(request)
    data = PecuarioDataProcessor.get_filtered_consumo(params)
    chart_capita = PecuarioDataProcessor.build_chart_por_tipo(data['capita'], 'consumo')
    chart_total = PecuarioDataProcessor.build_chart_consumo_total(data['total'])
    anio_ids = ConsumoCapita.objects.values_list('anio_id', flat=True).distinct()
    context = {
        'error_message': params['error_message'],
        'data_capita': data['capita'],
        'data_total': data['total'],
        'chart_capita': json.dumps(chart_capita),
        'chart_total': json.dumps(chart_total),
        'descripcion_modelo': descripcion_modelo,
        'anios': Anio.objects.filter(id__in=anio_ids).order_by('anio'),
    }
    return render(request, template, context)
