from django.db import models
from Anio.models import *
from Valor.models import *
from Mes.models import *
# Create your models here.

class TipoGanado(models.Model):
    tipo_ganado = models.CharField(max_length=200, blank=False,null=False)

    def __str__(self):
        return self.tipo_ganado
    
class FaenaPecuario(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
     tipo_ganado = models.ForeignKey(TipoGanado, on_delete=models.CASCADE, related_name='+')
     cabezas = models.CharField(max_length=200,null=False,blank=False)
     def __str__(self):
        return str(self.anio) + " " +  str(self.mes) + " " + str(self.valor) + " " + str(self.tipo_ganado) + " " + str(self.cabezas)
     

class StockPecuario(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
     tipo_ganado = models.ForeignKey(TipoGanado, on_delete=models.CASCADE, related_name='+')
     stock = models.CharField(max_length=200,null=False,blank=False)
     fecha_carga = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return str(self.anio) + " " +  str(self.mes) + " " + str(self.valor) + " " + str(self.tipo_ganado) + " " + str(self.stock)


class ConsumoCapita(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
     tipo_ganado = models.ForeignKey(TipoGanado, on_delete=models.CASCADE, related_name='+')
     consumo = models.CharField(max_length=200,null=False,blank=False)
     fecha_carga = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return str(self.anio) + " " +  str(self.mes) + " " + str(self.valor) + " " + str(self.tipo_ganado) + " " + str(self.consumo)

class ConsumoTotalProteina(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
     consumo_total = models.DecimalField(max_digits=8, decimal_places=2)
     fecha_carga = models.DateTimeField(auto_now_add=True)

class ProdDestIndustria(models.Model):
     anio = models.ForeignKey(Anio, on_delete=models.CASCADE, related_name='+')
     mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='+')
     valor = models.ForeignKey(Valor, on_delete=models.CASCADE, related_name='+')
     tipo_ganado = models.ForeignKey(TipoGanado, on_delete=models.CASCADE, related_name='+')
     produccion = models.CharField(max_length=200,null=False,blank=False)
     fecha_carga = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return str(self.anio) + " " +  str(self.mes) + " " + str(self.valor) + " " + str(self.tipo_ganado) + " " + str(self.produccion)
    


