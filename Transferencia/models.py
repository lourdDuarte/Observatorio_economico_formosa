from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *
# Create your models here.


class Transferencia(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    recaudacion = models.CharField(max_length=200,blank=False,null=False)
    total_millones = models.CharField(max_length=200,blank=False,null=False)
    variacion_anual_nominal = models.CharField(max_length=200,blank=False,null=False)
    variacion_anual_real = models.CharField(max_length=200,blank=False,null=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True) 

    def __str__(self):
         return str(self.anio)+ " " + str(self.mes) +  " " + str(self.valor) + " "   + str(self.variacion_anual_nominal) + " " + str(self.variacion_anual_real)