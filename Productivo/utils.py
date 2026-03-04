from Productivo.models import IndicadoresPrecioCultivo, TipoCultivo
from django.shortcuts import render
from Mes.models import *
import json
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any
from collections import defaultdict
from django.db.models import QuerySet
from Anio.models import Anio
from observatorioeconomico.utils import  get_default_anio_id_for_model



class ProductivoDataProcessor:

    # Constantes de configuración
    
    DEFAULT_VALUE = 1

    @staticmethod
    def get_data_variaciones(**kwargs) -> dict:
        return IndicadoresPrecioCultivo.objects.select_related(
            'mes', 'anio', 'tipo_cultivo'
        ).values(
            'mes__mes',
            'anio__anio',
            'tipo_cultivo__tipo_cultivo',
            'precio_nacional',
            'precio_internacional',
            'variacion_mensual',
            'variacion_fob'
        ).filter(**kwargs)

    @classmethod
    def get_default_year(cls, tipo_cultivo) -> int:
        return get_default_anio_id_for_model(
            IndicadoresPrecioCultivo,
            base_filters={
                "tipo_cultivo_id": tipo_cultivo,
                
            }
    )

    @classmethod
    def get_filtered_data(cls, tipo_cultivo, params: Dict[str, Any]) -> QuerySet:

        if params['is_valid']:
            return cls.get_data_variaciones(
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                tipo_cultivo_id=tipo_cultivo,
            ).order_by('anio__anio', 'mes__id')

        else:
            default_year = cls.get_default_year(tipo_cultivo)

            return cls.get_data_variaciones(
                anio_id=default_year,
                tipo_cultivo_id=tipo_cultivo,
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
    
  
    


def diccionario(queryset):
    variacion_mensual = []
    variacion_fob = []
    
    meses = []

    # Para mantener el orden, usamos listas separadas para cada región con su mes
    meses_var = []
   
    for item in queryset:
        mes = item['mes__mes'] + " " +  str(item['anio__anio'])
        var_mensual = float(item['variacion_mensual'])
        var_fob = float(item['variacion_fob'])

        
        variacion_mensual.append(var_mensual)
        variacion_fob.append(var_fob)
        meses_var.append(mes)
        
         

    # Obtener la cantidad mínima común
    minimo = min(len(variacion_mensual), len(variacion_fob))

    # Recortar todas las listas al mismo tamaño
    datos = {
        'meses': meses_var[:minimo],  # o meses_nacional[:minimo], ambos deberían coincidir en orden
        'Valor mensual': variacion_mensual[:minimo],
        'Valor fob': variacion_fob[:minimo],
        
    }

    return datos

def process_productivo_data(request:HttpRequest, tipo_cultivo, context_keys: Dict[str, str],descripcion_modelo:str, template: str) -> HttpResponse:
    
    processor = ProductivoDataProcessor
    
    meses = Mes.objects.all()

    params = processor.procces_request_parameters(request)
   
    
    data_variacion = processor.get_filtered_data(tipo_cultivo, params)
    
    diccionario_variacion = diccionario(data_variacion)
    
    anios = Anio.objects.all().order_by('anio')

    nombre_cultivo = TipoCultivo.objects.values('tipo_cultivo').filter(id = tipo_cultivo).first()

    
    # Construir contexto
    context = {
        'error_message': params['error_message'],
        context_keys['data_variacion']: data_variacion,
        context_keys['diccionario_variacion']: diccionario_variacion,
        'descripcion_modelo': descripcion_modelo,
        'meses': meses,
        'anios': anios,
        'tipo_cultivo': tipo_cultivo,
        'nombre_cultivo': nombre_cultivo
    }
    
    return render(request, template, context)





