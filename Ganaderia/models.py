from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *
# Create your models here.

class TipoGanado(models.Model):
    tipo_ganado = models.CharField(max_length=200, blank=False,null=False)

    def __str__(self):
        return self.tipo_ganado
    

class StockConsumoGanado(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     TipoCultivo = models.ForeignKey(TipoCultivo, on_delete=models.CASCADE, related_name='+')
     precio_nacional = models.CharField(max_length=200,null=False,blank=False)
     precio_internacional = models.CharField(max_length=200,null=False,blank=False)
     variacion_mensual = models.CharField(max_length=200,null=False,blank=False)
     variacion_fob = models.CharField(max_length=200,null=False,blank=False)
     fecha_actualizacion = models.DateTimeField(auto_now=True) 
