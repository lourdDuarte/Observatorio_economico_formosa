from typing import Dict, Any
from collections import defaultdict
import json

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import OuterRef, Subquery, QuerySet
from Anio.models import Anio
from Supermercado.models import Variacion, Total, Mes
from observatorioeconomico.utils import get_default_anio_id_for_model_with_valores



class SupermercadoDataProcessor:
    PRICE_TYPE_CORRIENTE = 2
    PRICE_TYPE_CONSTANTE = 1
    REGION_FORMOSA = 'Formosa'
    REGION_NACIONAL = 'Nacional'

    @staticmethod
    def get_variacion_data(**filters) -> QuerySet:
        """
        Función que genera la consulta (y subconsulta) a la bd.
        """

        venta_total_subquery = Total.objects.filter(
            anio=OuterRef('anio'),
            mes=OuterRef('mes'),
            valor=OuterRef('valor'),
            tipoPrecio=OuterRef('tipoPrecio')
        ).values('venta_total')[:1]

        return Variacion.objects.select_related(
            'mes', 'anio', 'valor', 'tipoPrecio'
        ).annotate(
            venta_total=Subquery(venta_total_subquery)
        ).values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'variacion_interanual',
            'variacion_intermensual',
            'venta_total'
        ).filter(**filters)

    @classmethod
    def get_default_year(cls, tipo_precio: int) -> int:
        return get_default_anio_id_for_model_with_valores(
            Variacion,
            field_name="valor_id",
            required_values=[1, 2],
            extra_filters={
                "tipoPrecio_id": tipo_precio
            }
    )

    @classmethod
    def get_filtered_data(cls, tipo_precio: int, params: Dict[str, Any]) -> QuerySet:

        filtros = {
            'tipoPrecio_id': tipo_precio
        }

        if params['is_valid']:
            filtros.update({
                'anio_id__gte': params['anio_inicio'],
                'anio_id__lte': params['anio_fin']
            })
        else:
           filtros['anio_id'] = cls.get_default_year(tipo_precio)

        return cls.get_variacion_data(**filtros).order_by('anio__anio', 'mes__id')


    @classmethod
    def process_request_parameters(cls, request: HttpRequest) -> Dict[str, Any]:

        
        """
            Procesa y valida los parámetros de año enviados a través de una solicitud HTTP GET.

            Extrae los parámetros `anio_inicio` y `anio_fin` desde la query string del request,
            la funcion busca asegurar:
            - Ambos años estén presentes.
            - Los valores sean numéricos válidos.
            - El año de inicio no sea mayor que el de fin.

            Returns:
                dict: Un diccionario con las siguientes claves:
                    - anio_inicio (int or None): Año inicial, si fue proporcionado y válido.
                    - anio_fin (int or None): Año final, si fue proporcionado y válido.
                    - is_valid (bool): Indica si los parámetros son válidos para usar en filtros.
                    - error_message (str or None): Mensaje descriptivo si hubo un error en los filtros,
                    o `None` si no hay error (incluido el caso de primer acceso sin filtros).
        """

        anio_inicio = request.GET.get('anio_inicio')
        anio_fin = request.GET.get('anio_fin')
        filtros = {}

        if not anio_inicio and not anio_fin:
            return {'anio_inicio': None, 'anio_fin': None, 'is_valid': False, 'error_message': None}

        try:
            if anio_inicio:
                filtros['anio_inicio'] = int(anio_inicio)
            if anio_fin:
                filtros['anio_fin'] = int(anio_fin)

            if 'anio_inicio' in filtros and 'anio_fin' in filtros:
                if filtros['anio_fin'] < filtros['anio_inicio']:
                    return {**filtros, 'is_valid': False, 'error_message': "El año de fin no puede ser menor que el de inicio."}
                return {**filtros, 'is_valid': True, 'error_message': None}

            return {**filtros, 'is_valid': False, 'error_message': "Debe seleccionar ambos años para aplicar el filtro."}

        except ValueError:
            return {'anio_inicio': None, 'anio_fin': None, 'is_valid': False, 'error_message': "Los filtros ingresados no son válidos."}

    
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, Dict[int, list]]:
        chart_data = {
            SupermercadoDataProcessor.REGION_FORMOSA: defaultdict(list),
            SupermercadoDataProcessor.REGION_NACIONAL: defaultdict(list),
        }

        for item in data_variacion:
            anio = item['anio__anio']
            venta_total = item['venta_total'] or 0
            region = item['valor__valor']

            if region in chart_data:
                chart_data[region][anio].append(venta_total)

        return {
            region: dict(data) for region, data in chart_data.items()
        }


def construir_diccionario(queryset: QuerySet) -> Dict[str, list]:
    data = {
        'Valor intermensual Formosa': [],
        'Valor interanual Formosa': [],
        'Valor intermensual Nacional': [],
        'Valor interanual Nacional': [],
    }

    meses_formosa, meses_nacional = [], []

    for item in queryset:
        mes_str = f"{item['mes__mes']} {item['anio__anio']}"
        region = item['valor__valor']
        intermensual = float(item['variacion_intermensual'])
        interanual = float(item['variacion_interanual'])

        if region == SupermercadoDataProcessor.REGION_FORMOSA:
            data['Valor intermensual Formosa'].append(intermensual)
            data['Valor interanual Formosa'].append(interanual)
            meses_formosa.append(mes_str)
        elif region == SupermercadoDataProcessor.REGION_NACIONAL:
            data['Valor intermensual Nacional'].append(intermensual)
            data['Valor interanual Nacional'].append(interanual)
            meses_nacional.append(mes_str)

    minimo = min(
        len(data['Valor intermensual Formosa']),
        len(data['Valor intermensual Nacional'])
    )

    data['meses'] = meses_formosa[:minimo]
    for key in list(data.keys()):
        if key != 'meses':
            data[key] = data[key][:minimo]

    return data


def process_supermercado_data(
    request: HttpRequest,
    tipo_precio: int,
    context_keys: Dict[str, str],
    descripcion_modelo: str,
    template: str
) -> HttpResponse:
    processor = SupermercadoDataProcessor()
    params = processor.process_request_parameters(request)
    data_variacion = processor.get_filtered_data(tipo_precio, params)
    dicc_variacion = construir_diccionario(data_variacion)
    chart_data = processor.process_chart_data_totales(data_variacion)
    anio_ids = Variacion.objects.values_list('anio_id', flat=True).distinct()

    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: dicc_variacion,
        'data_chart_formosa': json.dumps(chart_data[SupermercadoDataProcessor.REGION_FORMOSA]),
        'data_chart_nacional': json.dumps(chart_data[SupermercadoDataProcessor.REGION_NACIONAL]),
        'descripcion_modelo': descripcion_modelo,
        'meses': Mes.objects.all(),
        'anios': Anio.objects.filter(id__in=anio_ids).order_by('anio'),
    }

    return render(request, template, context)
