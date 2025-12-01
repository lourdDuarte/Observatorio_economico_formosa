from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *

# Create your models here.
class TipoTarifa(models.Model):
    tipo_tarifa = models.CharField(max_length=200, blank=False, null=False)
    
    def __str__(self):
        return str(self.tipo_tarifa)


class Refsa(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tarifa = models.ForeignKey(TipoTarifa, on_delete=models.CASCADE, related_name='+')
    cantidad_usuarios = models.CharField(max_length=200, null=False, blank=False)
    variacion_bimestral = models.CharField(max_length=200, null=False, blank=False)
    variacion_interanual= models.CharField(max_length=200, null=False, blank=False)


    def __str__(self):
        return str(self.anio) + " " + str(self.mes) + " "  + str(self.valor) + " " + str(self.variacion_bimestral) + "-" + str(self.variacion_interanual)

class Cammesa(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tarifa = models.ForeignKey(TipoTarifa, on_delete=models.CASCADE, related_name='+')
    demanda = models.CharField(max_length=200, null=False, blank=False)
    variacion_interanual = models.CharField(max_length=200, null=False, blank=False)
    variacion_intermensual = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.anio) + " " + str(self.mes) + " "  + str(self.valor) + " " + str(self.variacion_interanual) + "-" + str(self.variacion_intermensual)