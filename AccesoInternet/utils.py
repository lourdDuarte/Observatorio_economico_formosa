from .models import TipoAcceso, AccesoInternet
from observatorioeconomico.utils import  get_default_anio_id_for_model_with_valores
from django.shortcuts import render
from Mes.models import *
import json
from django.db.models import QuerySet, Count
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from collections import defaultdict
from django.db.models import QuerySet
from Anio.models import Anio
from observatorioeconomico.utils import  get_default_anio_id_for_model_with_valores

class AccesoInternetProcessor:
    DEFAULT_VALUE = 1

    @staticmethod
    def get_data_variaciones(**kwargs) -> dict:
        return AccesoInternet.objects.select_related(
            'mes', 'anio', 'valor', 'tipo_acceso'
        ).values(
            'mes__mes',
            'anio__anio',
            'valor__valor',
            'tipo_acceso__tipo',
            'cantidad',
            'variacion_interanual'
            
        ).filter(**kwargs)

    @classmethod
    def get_default_year(cls) -> Optional[int]:
        """
        Retorna el ID del año más reciente que tenga datos de todos los tipos de acceso.
        """
        total_tipo_internet = AccesoInternet.objects.values(
            'tipo_acceso'
        ).distinct().count()

        resultado = (
           AccesoInternet.objects
            .values('anio_id')
            .annotate(cant_internet=Count('tipo_acceso', distinct=True))
            .filter(cant_internet=total_tipo_internet)
            .order_by('-anio_id')
            .first()
        )
        return resultado['anio_id'] if resultado else None

    @classmethod
    def get_anios_completos_ids(cls):
        """
        Retorna los IDs de años donde TODOS los tipos de acceso tienen datos cargados.
        """
        total_tipos = AccesoInternet.objects.values('tipo_acceso').distinct().count()
        return (
            AccesoInternet.objects
            .values('anio_id')
            .annotate(cant_tipos=Count('tipo_acceso', distinct=True))
            .filter(cant_tipos=total_tipos)
            .values_list('anio_id', flat=True)
        )
    
    @classmethod
    def get_filtered_data(cls, params: Dict[str, Any]) -> QuerySet:

        if params['is_valid']:
            return cls.get_data_variaciones(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
            ).order_by('anio__anio', 'mes__id')

        else:
            default_year = cls.get_default_year()

            return cls.get_data_variaciones(
                anio_id=default_year,
               
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
    def process_chart_cantidad(data_cantidades: QuerySet) -> Dict[str, Any]:
        formosa = defaultdict(lambda: defaultdict(dict))
        nacional = defaultdict(lambda: defaultdict(dict))

        for item in data_cantidades:
            mes = item['mes__mes']
            anio = str(item['anio__anio'])
            cantidad = item['cantidad']
            tipo_acceso = item['tipo_acceso__tipo']
            valor = item['valor__valor']

            if cantidad is not None:
                if valor == 'Formosa':
                    formosa[tipo_acceso][anio][mes] = int(cantidad)
                elif valor == 'Nacional':
                    nacional[tipo_acceso][anio][mes] = int(cantidad)

        return {
            'Formosa': dict(formosa),
            'Nacional': dict(nacional),
        }


    @staticmethod
    def build_chart_data(queryset) -> Dict[str, Any]:
        items = list(queryset)
        meses = []
        data = {}

        for item in items:
            label = f"{item['mes__mes']} {item['anio__anio']}"
            if label not in meses:
                meses.append(label)

        for item in items:
            serie = f"{item['tipo_acceso__tipo']} {item['valor__valor']}"
            if serie not in data:
                data[serie] = {m: 0 for m in meses}

        for item in items:
            label = f"{item['mes__mes']} {item['anio__anio']}"
            serie = f"{item['tipo_acceso__tipo']} {item['valor__valor']}"
            data[serie][label] = float(item['variacion_interanual'])

        # Eliminar series que tienen todos los valores en 0
        data = {serie: valores for serie, valores in data.items()
                if any(v != 0.0 for v in valores.values())}

        if not data:
            return {'meses': []}

        # Cortar en el primer mes donde alguna serie no tiene dato (valor 0)
        cutoff_idx = len(meses)
        for i, mes in enumerate(meses):
            if not all(valores[mes] != 0.0 for valores in data.values()):
                cutoff_idx = i
                break

        meses = meses[:cutoff_idx]

        resultado = {'meses': meses}
        for serie, valores in data.items():
            resultado[serie] = [valores[m] for m in meses]

        return resultado

def process_acceso_data(request:HttpRequest,  context_keys: Dict[str, str],descripcion_modelo:str, template: str) -> HttpResponse:


    processor = AccesoInternetProcessor
    meses = Mes.objects.all()

    params = processor.procces_request_parameters(request)
    data_variacion = processor.get_filtered_data(params)
    diccionario_variacion = processor.build_chart_data(data_variacion)
    context_chart = processor.process_chart_cantidad(data_variacion)
    anio_ids_completos = processor.get_anios_completos_ids()

    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: diccionario_variacion,
        'chart_data_formosa_json': json.dumps(context_chart['Formosa']),
        'chart_data_nacional_json': json.dumps(context_chart['Nacional']),
        'descripcion_modelo': descripcion_modelo,
        'meses': meses,
        'anios': Anio.objects.filter(id__in=anio_ids_completos).order_by('anio'),
    }
    
    return render(request, template, context)

    