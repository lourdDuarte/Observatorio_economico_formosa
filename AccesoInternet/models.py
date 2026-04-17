from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *

class TipoAcceso(models.Model):
    tipo = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.tipo
    

class AccesoInternet(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tipo_acceso = models.ForeignKey(TipoAcceso, on_delete=models.CASCADE, related_name='+')
    cantidad = models.CharField(max_length=200, null=False, blank=False)
    variacion_interanual = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
                return str(self.anio) + " " + str(self.mes) + " "  + str(self.valor) + " " +  str(self.tipo_acceso) + " " + str(self.cantidad)