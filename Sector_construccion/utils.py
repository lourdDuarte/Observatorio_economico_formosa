
from Sector_construccion.models import Indicadores, SectorConstruccion
from django.shortcuts import render
from Mes.models import *
from typing import Dict, Any, Optional
from django.http import HttpRequest, HttpResponse
from Anio.views import *
from collections import defaultdict
from django.db.models import OuterRef, Subquery, QuerySet



class ConstruccionProcessor:

    # Constantes de configuración
    DEFAULT_YEAR = 7
    DEFAULT_VALUE = 1

   



    @staticmethod
    def get_data_variaciones(**kwargs) -> dict:
        

        
        return SectorConstruccion.objects.select_related('mes', 'anio', 'valor').values(
            'mes__mes',
            'mes',
            'anio__anio',
            'valor__valor',
            'total_empresas',
            'total_puesto_trabajo',
            'salario_promedio'
        
        ).filter(**kwargs)
    
    @staticmethod
    def get_data_indicadores(**kwargs) -> dict:
        

        
        return Indicadores.objects.select_related('mes', 'anio', 'valor').values(
            'mes__mes',
            'mes',
            'anio__anio',
            'valor__valor',
            'tipo_dato',
            'variacion_interanual',
            'variacion_intermensual'
            
        
        ).filter(**kwargs)
    
        


    @classmethod
    def process_and_validate_ipc_data(cls,data):
            meses_vistos = set()  # Almacena pares (mes, año)

            #Validación de Meses Repetidos 
            for item_validacion in data:
                mes_nombre = item_validacion['mes__mes']
                anio = item_validacion['anio__anio']
                valor_tipo = item_validacion['valor__valor']
                
                clave_mes_anio = (mes_nombre, anio)
                
                if clave_mes_anio in meses_vistos:
                    pass
                else:
                    #Mes encontrado por primera vez
                    meses_vistos.add(clave_mes_anio)
            
            grouped_data = defaultdict(lambda: {'Formosa': None, 'Nacional': None, 'mes_nombre': None, 'anio': None})

            for item in data:
                mes_id = item['mes']
                mes_nombre = item['mes__mes']
                anio = item['anio__anio']
                valor_tipo = item['valor__valor'] 
                salario = item['salario_promedio']

                clave = (anio, mes_id)

                grouped_data[clave]['mes_nombre'] = mes_nombre
                grouped_data[clave]['anio'] = anio

                if valor_tipo == 'Formosa':
                    grouped_data[clave]['Formosa'] = salario
                elif valor_tipo == 'Nacional':
                    grouped_data[clave]['Nacional'] = salario

            # Armamos la lista final, ordenando por año y mes
            final_chart_data = []

            for clave in sorted(grouped_data.keys()):  # Ordena por (año, mes_id)
                entry = grouped_data[clave]
                if entry['Formosa'] is not None and entry['Nacional'] is not None:
                    final_chart_data.append({
                        'mes': f"{entry['mes_nombre']} {entry['anio']}",
                        'salario_formosa': float(entry['Formosa']),
                        'salario_nacional': float(entry['Nacional'])
                    })

            return final_chart_data
    
    @classmethod
    def get_filtered_data(cls, value:int,  params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
           
            return cls.get_data_variaciones(
                valor_id = value,
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin']).order_by('anio__anio', 'mes__id')
        else:
            
            return cls.get_data_variaciones(
                anio_id=cls.DEFAULT_YEAR,
                valor_id = value
            )
        
    @classmethod
    def get_filtered_indicadores(cls, tipo_dato:int,  params: Dict[str, Any]) -> QuerySet:
        """
        Obtiene datos filtrados según los parámetros.
        
        Returns:
            QuerySet con los datos filtrados
        """
        if params['is_valid']:
           
            return cls.get_data_indicadores(
                tipo_dato = tipo_dato,
                anio_id__gte=params['anio_inicio'],
                anio_id__lte=params['anio_fin'],
                valor_id = params['valor']).order_by('anio__anio', 'mes__id')
        else:
            
            return cls.get_data_indicadores(
               anio_id=cls.DEFAULT_YEAR,
               tipo_dato = tipo_dato,
               valor_id = cls.DEFAULT_VALUE
            )
    @staticmethod
    def process_chart_data_totales(type_date, data_variacion: QuerySet) -> Dict[str, list]:
            """
            Procesa los datos para generar información de gráficos.
            
            Args:
                data_variacion: QuerySet con datos de variaciones
                
            Returns:
                Dict con datos organizados por año para gráficos
            """
            chart_totales = defaultdict(list)
            
            for item in data_variacion:
                anio = item['anio__anio']
                
                total = item[type_date]
                if total is not None:
                        
                    chart_totales[anio].append(total)
            
            return dict(chart_totales)

    @classmethod
    def procces_request_parameters(cls, request: HttpRequest,) -> Dict[str,any]:
        try:
            anio_inicio = request.GET.get('anio_inicio')
            anio_fin = request.GET.get('anio_fin')

            valor = request.GET.get('valor')
            if anio_inicio and anio_fin:
                return {
                    'anio_inicio': int(anio_inicio),
                    'anio_fin': int(anio_fin),
                    'valor':int(valor),
                    'is_valid' : True,
                    'error_message': None
                }
            else:
                return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'valor': None,
                    'is_valid' : False,
                    'error_message': None
                }

        except ValueError:
             return {
                    'anio_inicio': None,
                    'anio_fin': None,
                    'valor': None,
                    'is_valid' : False,
                    'error_message': False
                }
        
        


def process_construccion_data(request:HttpRequest, tipo_dato:int, value_totales:str, context_keys: Dict[str, str], template: str) -> HttpResponse:
    DEFAULT_FORMOSA = 1
    DEFAULT_NACION = 2
    
    meses = Mes.objects.all()

    processor = ConstruccionProcessor
    params = processor.procces_request_parameters(request)

    if params['valor'] is None:
        FILTER = DEFAULT_FORMOSA
    else:
        FILTER = params['valor']
   
    #context for template salarios
    
    salario_formosa = processor.get_filtered_data(DEFAULT_FORMOSA, params)
    salario_nacion = processor.get_filtered_data(DEFAULT_NACION,params)
   
    data_totales = processor.get_filtered_data(FILTER, params) 
    
    
    
    
    data_variacion_salario_table = salario_formosa | salario_nacion 
   
    final_chart_data = processor.process_and_validate_ipc_data(data_variacion_salario_table)


    # ******** puestos trabajo 
    indicadores_puestos_trabajo = processor.get_filtered_indicadores(tipo_dato, params)

    data_variacion_puestos_table = data_totales
    # Convertir a listas normales (si no lo están)
    lista_1 = list(indicadores_puestos_trabajo)
    lista_2 = list(data_variacion_puestos_table)

    # Crear un diccionario auxiliar para buscar por mes-año-valor
    dict_puestos = {
        (item['anio__anio'], item['mes'], item['valor__valor']): item
        for item in lista_2
    }

    # Unir la información
    contexto_unificado = []
    for item in lista_1:
        clave = (item['anio__anio'], item['mes'], item['valor__valor'])
        puestos_info = dict_puestos.get(clave, {})  # puede venir vacío si no hay match

        # Crear el nuevo diccionario unificado
        combinado = {
            'anio': item['anio__anio'],
            'mes': item['mes__mes'],
            
            'valor': item['valor__valor'],
            'variacion_intermensual': item.get('variacion_intermensual'),
            'variacion_interanual': item.get('variacion_interanual'),
            'total_puesto_trabajo': puestos_info.get('total_puesto_trabajo'),
        }

        contexto_unificado.append(combinado)
    if params['is_valid']:
        type_graphic = 1
        chart_totales = processor.process_chart_data_totales(value_totales,  data_totales)
        
        
    else:
        type_graphic = 0
        chart_totales = {}
       
    context = {
        'error_message': params['error_message'],
        context_keys['final_chart_data']: final_chart_data,
        context_keys['data_variacion_salario_table']: data_variacion_salario_table,
        context_keys['salario_formosa']:salario_formosa,
         
        context_keys['chart_totales']:chart_totales,
        context_keys['indicadores_puestos_trabajo']: indicadores_puestos_trabajo,
        
        context_keys['data_variacion_puestos_table']: contexto_unificado,
        context_keys['type_graphic']: type_graphic,
        'meses': meses,
    }
        
    return render(request, template, context)
