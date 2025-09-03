from django.db import models

from Anio.models import *
from Valor.models import *
from Mes.models import *

# Create your models here.
class TipoMovimiento(models.Model):
    tipo_movimiento = models.CharField(max_length=200, blank=False, null=False)


    def __str__(self):
        return self.tipo_movimiento
    
class TipoVehiculo(models.Model):
    tipo_vehiculo = models.CharField(max_length=200, blank=False, null=False)

    def __str__(self):
        return self.tipo_vehiculo
    
class Indicadores(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    movimiento_vehicular = models.ForeignKey(TipoMovimiento, on_delete=models.CASCADE, related_name='+')
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE, related_name='+')
    total = models.CharField(max_length=200, null=False, blank=False)
    total_acumulado = models.CharField(max_length=200, null=False, blank=False)
    variacion_interanual = models.CharField(max_length=200, null=False, blank=False)
    variacion_intermensual = models.CharField(max_length=200, null=False, blank=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True) 


    def __str__(self):
        return str(self.anio) + " " + str(self.mes) + " "  + str(self.valor) + " " + str(self.total_acumulado) + " " +str(self.variacion_interanual) + "-" + str(self.variacion_intermensual)