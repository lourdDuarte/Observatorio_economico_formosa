from django.contrib import admin
from .models import *
# Register your models here.

def get_model_total_vehiculo(mes, anio, valor, movimiento_vehicular, tipo_vehiculo,value):
    return Indicadores.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        movimiento_vehicular_id=movimiento_vehicular,
        tipo_vehiculo_id =  tipo_vehiculo
    ).values(value).first()

@admin.register(Indicadores)
class PatentamientoIndicadorAdmin(admin.ModelAdmin):
    list_filter = ['anio__anio', 'mes__mes', 'movimiento_vehicular','tipo_vehiculo__tipo_vehiculo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor', 'movimiento_vehicular', 'tipo_vehiculo','total', 'variacion_interanual', 'variacion_intermensual']
    list_editable = ['valor', 'movimiento_vehicular', 'tipo_vehiculo','total', 'variacion_interanual', 'variacion_intermensual'] 
    list_per_page = 12
    exclude = ['total_acumulado', 'variacion_interanual', 'variacion_intermensual']

    def save_model(self, request, obj, form, change):

        data_indicadores = {
            'anio_id': obj.anio.id,
            'mes_id': obj.mes.id,
            'valor_id': obj.valor.id,
            'movimiento_vehicular_id': obj.movimiento_vehicular_id,
            'tipo_vehiculo_id': obj.tipo_vehiculo_id,
            'total': obj.total
        }

        indicador_intermensual = {}
        indicador_interanual = {}
        

        anio_anterior = int(data_indicadores['anio_id']) - 1

        
        if data_indicadores['mes_id'] == 1:
            mes_anterior = 12
            var_acumulado = data_indicadores['total']
            data_intermensual = get_model_total_vehiculo(

                mes = mes_anterior,
                anio = anio_anterior,
                valor= data_indicadores['valor_id'],
                movimiento_vehicular= data_indicadores['movimiento_vehicular_id'],
                tipo_vehiculo= data_indicadores['tipo_vehiculo_id'],
                value = 'total'
            )
        else:
            mes_anterior = data_indicadores['mes_id'] - 1
            data_intermensual = get_model_total_vehiculo(
                mes = mes_anterior,
                anio = data_indicadores['anio_id'],
                valor= data_indicadores['valor_id'],
                movimiento_vehicular= data_indicadores['movimiento_vehicular_id'],
                tipo_vehiculo= data_indicadores['tipo_vehiculo_id'],
                value = 'total'
            )

            data_acumulado = get_model_total_vehiculo(
                mes = mes_anterior,
                anio = data_indicadores['anio_id'],
                valor= data_indicadores['valor_id'],
                movimiento_vehicular= data_indicadores['movimiento_vehicular_id'],
                tipo_vehiculo= data_indicadores['tipo_vehiculo_id'],
                value = 'total_acumulado'
            )

            acumulado_anterior = {
                'acumulado': data_acumulado['total_acumulado']
            }
           
            var_acumulado = int(acumulado_anterior['acumulado']) + int(data_indicadores['total'])

        data_interanual = get_model_total_vehiculo(
            mes = data_indicadores['mes_id'],
            anio = anio_anterior,
            valor= data_indicadores['valor_id'],
            movimiento_vehicular= data_indicadores['movimiento_vehicular_id'],
            tipo_vehiculo= data_indicadores['tipo_vehiculo_id'],
            value = 'total'
        )

        
        
        if data_intermensual:
            indicador_intermensual =  {
                'totales': data_intermensual['total']
        }
        

        if data_interanual:
            indicador_interanual = {
                
                'totales': data_interanual['total'],
                
            }

    
    

        var_intermensual = int(data_indicadores['total']) / int(indicador_intermensual['totales']) * 100 - 100
        
        var_interanual = int(data_indicadores['total']) / int(indicador_interanual['totales']) * 100 - 100

        obj.variacion_interanual= round(var_intermensual,1)
        obj.variacion_intermensual = round(var_interanual,1)
        obj.total_acumulado = round(var_acumulado)
        
     
        super().save_model(request, obj, form, change)