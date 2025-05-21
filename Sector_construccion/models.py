from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *

# Create your models here.

class TipoDato(models.Model):
    tipo_dato = models.CharField(max_length=200, blank=False, null=False)

    def __str__ (self):
        return self.tipo_dato
    

class SectorConstruccion(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    total_empresas = models.CharField(max_length=200, blank=False, null=False)
    total_puesto_trabajo = models.CharField(max_length=200, blank=False, null=False)
    salario_promedio = models.CharField(max_length=200, blank=False, null=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True) 

    def __str__(self):
            return str(self.anio) + " " + str(self.mes) +  " "  + str(self.valor)  + "-" + str(self.salario_promedio)
    
class Indicadores(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tipo_dato = models.ForeignKey(TipoDato, on_delete=models.CASCADE, related_name='+')
    variacion_interanual = models.CharField(max_length=200, null=False, blank=False)
    variacion_intermensual = models.CharField(max_length=200, null=False, blank=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return str(self.anio) + " " + str(self.mes) +  " "  + str(self.valor) + " " +  str(self.variacion_interanual) + "-" + str(self.variacion_intermensual)