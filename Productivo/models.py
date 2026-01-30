from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *
# Create your models here.

class TipoCultivo(models.Model):
    tipo_cultivo = models.CharField(max_length=200, blank=False,null=False)

    def __str__(self):
        return self.tipo_cultivo
    

class CampaniaCultivo(models.Model):
    campania = models.CharField(max_length=200, blank=False,null=False)

    def __str__(self):
        return self.campania
    

class IndicadoresPrecioCultivo(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     tipo_cultivo = models.ForeignKey(TipoCultivo, on_delete=models.CASCADE, related_name='+')
     precio_nacional = models.CharField(max_length=200,null=False,blank=False)
     precio_internacional = models.CharField(max_length=200,null=False,blank=False)
     variacion_mensual = models.CharField(max_length=200,null=False,blank=False)
     variacion_fob = models.CharField(max_length=200,null=False,blank=False)
     fecha_actualizacion = models.DateTimeField(auto_now=True) 

     def __str__(self):
        return (str(self.tipo_cultivo) + " " + str(self.anio) + " " + str(self.mes) + " " + str(self.precio_nacional) + " " + str(self.precio_internacional))



class ProduccionCampaniaCultivo(models.Model):
     tipo_cultivo = models.ForeignKey(TipoCultivo, on_delete=models.CASCADE, related_name='+')
     campania = models.ForeignKey(CampaniaCultivo, on_delete=models.CASCADE, related_name='+')
     valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
     superficie_sembrada = models.CharField(max_length=200,null=False,blank=False)
     superficie_cosechada = models.CharField(max_length=200,null=False,blank=False)
     produccion = models.CharField(max_length=200,null=False,blank=False)
     fecha_actualizacion = models.DateTimeField(auto_now=True) 


class ParticipacionProdFormosa(models.Model):
     tipo_cultivo = models.ForeignKey(TipoCultivo, on_delete=models.CASCADE, related_name='+')
     campania = models.ForeignKey(CampaniaCultivo, on_delete=models.CASCADE, related_name='+')
     participacion = models.CharField(max_length=200,null=False,blank=False)

