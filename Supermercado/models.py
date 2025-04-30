from django.db import models

# Create your models here.
from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *


class TipoPrecio(models.Model):
    tipo = models.CharField(max_length=200, blank=False,null=False)

    def __str__(self):
        return self.tipo

class TipoArticulo(models.Model):
    articulo = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.articulo)

class Total(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
     tipoPrecio = models.ForeignKey(TipoPrecio, on_delete=models.CASCADE, related_name='+')
     venta_total = models.CharField(max_length=200,null=False,blank=False)

     def __str__(self):
        return self.venta_total

class Variacion(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tipoPrecio = models.ForeignKey(TipoPrecio, on_delete=models.CASCADE, related_name='+')
    variacion_interanual = models.CharField(max_length=200, null=False, blank=False)
    variacion_intermensual = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.anio) + str(self.mes)  + str(self.tipoPrecio) + str(self.variacion_interanual) + str(self.variacion_intermensual)

  

class VentaArticulo(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    articulo =  models.ForeignKey(TipoArticulo, on_delete=models.CASCADE, related_name='+')
    tipoPrecio = models.ForeignKey(TipoPrecio, on_delete=models.CASCADE, related_name='+')
    total = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.anio) + " " + str(self.mes) + str(self.articulo) + "-" + str(self.total)


class VentaParticipacion(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    tipoPrecio = models.ForeignKey(TipoPrecio, on_delete=models.CASCADE, related_name='+')
    acumulado_total = models.CharField(max_length=200, null=False, blank=False)
    participacion_total = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.acumulado_total + "-" + self.participacion_total
    
class Indicadores(models.Model):
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
    valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
    cantidad_operaciones = models.CharField(max_length=200, null=False, blank=False)
    variacion_interanual = models.CharField(max_length=200, null=False, blank=False)
    variacion_intermensual = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.anio) + " - " + str(self.mes) + " - " + str(self.valor) + " - " + self.variacion_interanual + " - " + self.variacion_intermensual