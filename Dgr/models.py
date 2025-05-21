from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *
# Create your models here.

class Tipo(models.Model):
    tipo = models.CharField(max_length=200,blank=False,null=False)

    def __str__(self):
        return self.tipo
    




class Indicadores(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name='+')
    variacion_interanual = models.CharField(max_length=200,blank=False,null=False)
    variacion_intermensual = models.CharField(max_length=200,blank=False,null=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True) 

    def __str__(self):
            return str(self.anio) + " " + str(self.mes) + " " + str(self.tipo) + " "  + str(self.valor) + " " + str(self.variacion_interanual) + " " + str(self.variacion_intermensual)



class Recaudacion(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name='+')
    recaudacion = models.CharField(max_length=200,blank=False,null=False)
    recaudacion_acumulada = models.CharField(max_length=200,blank=False,null=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True) 

    def __str__(self):
            return str(self.anio) + " " + str(self.mes) + " " + str(self.tipo) + " "  + str(self.valor) + " " + str(self.recaudacion) + " " + str(self.recaudacion_acumulada)