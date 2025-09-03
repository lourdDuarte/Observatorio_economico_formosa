from django.contrib import admin
from .models import *
# Register your models here.

# admin.site.register(VentaArticulo) 
# admin.site.register(VentaParticipacion) 
# admin.site.register(Indicadores)  

#admin.site.register(Variacion)

@admin.register(Variacion)
class SupermercadoVariacionAdmin(admin.ModelAdmin):
    search_fields = ['anio__anio','tipoPrecio__tipo', 'valor__valor',  'variacion_interanual', 'variacion_intermensual']
    list_filter = ['anio__anio', 'mes__mes', 'tipoPrecio__tipo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor',  'variacion_interanual', 'variacion_intermensual']
    list_editable = ['mes', 'valor',  'variacion_interanual', 'variacion_intermensual'] 
    list_per_page = 12

def get_model_total_supermercado(mes, anio, valor, tipo_precio):
    return Total.objects.filter(
        mes_id=mes,
        anio_id=anio,
        valor_id=valor,
        tipoPrecio_id=tipo_precio
    ).values("venta_total").first()
 
@admin.register(Total)
class SupermercadoTotalAdmin(admin.ModelAdmin):
    search_fields = ['anio__anio','tipoPrecio__tipo', 'valor__valor',  'venta_total']
    list_filter = ['anio__anio', 'mes__mes', 'tipoPrecio__tipo', 'valor__valor']
    ordering = ['-anio', 'mes']
    list_display = ['anio', 'mes', 'valor', 'tipoPrecio', 'venta_total']
    list_editable = ['valor', 'tipoPrecio', 'venta_total'] 
    list_per_page = 12
    
    def save_model(self, request, obj, form, change):

        data_indicadores = {
            'anio_id': obj.anio.id,
            'mes_id': obj.mes.id,
            'valor_id': obj.valor.id,
            'tipoPrecio_id': obj.tipoPrecio_id,
            'total_venta': obj.venta_total
        }

 
        
        

        indicador_intermensual = {}
        indicador_interanual = {}
        anio_anterior = int(data_indicadores['anio_id']) - 1

        if data_indicadores['mes_id'] == 1: 
            mes_anterior = 12
            data_intermensual =  get_model_total_supermercado(
                mes= mes_anterior,
                anio=anio_anterior,
                valor= data_indicadores['valor_id'],
                tipo_precio=data_indicadores['tipoPrecio_id'])
        else:
            mes_anterior = int(data_indicadores['mes_id']) - 1 # se va utilizar para var intermensual
            data_intermensual = get_model_total_supermercado(
                mes= mes_anterior,
                anio= data_indicadores['anio_id'],
                valor= data_indicadores['valor_id'],
                tipo_precio=data_indicadores['tipoPrecio_id'])
            

        data_interanual = get_model_total_supermercado(
            mes =data_indicadores['mes_id'], 
            anio =anio_anterior,
            valor = data_indicadores['valor_id'],
            tipo_precio =data_indicadores['tipoPrecio_id'])
        
        if data_intermensual:
            indicador_intermensual =  {
                'ventas_total': data_intermensual['venta_total']
        }
        

        if data_interanual:
            indicador_interanual = {
                
                'ventas_total': data_interanual['venta_total'],
                
            }

        print(f"venta total actual: ",float(data_indicadores['total_venta']), 
              "venta total extraida: ",float(indicador_intermensual['ventas_total']))
        

        var_intermensual = float(data_indicadores['total_venta']) / float(indicador_intermensual['ventas_total']) * 100 - 100
        
        var_interanual = float(data_indicadores['total_venta']) / float(indicador_interanual['ventas_total']) * 100 - 100

        Variacion.objects.update_or_create(
            anio=Anio.objects.get(pk= data_indicadores['anio_id']),
            mes=Mes.objects.get(pk=data_indicadores['mes_id']),
            valor=Valor.objects.get(pk=data_indicadores['valor_id']),
            tipoPrecio=TipoPrecio.objects.get(pk=data_indicadores['tipoPrecio_id']),
               
            defaults={
                "variacion_intermensual": round(var_intermensual, 1),
                "variacion_interanual": round(var_interanual, 1),
            }
        )

      
        
        super().save_model(request, obj, form, change)