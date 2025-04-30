from django.db import models

# Create your models here.

class Valor(models.Model):
    valor = models.CharField(max_length=200,blank=False,null=False)

    def __str__(self):
        return self.valor
    

class Trimestre(models.Model):
    trimestre = models.CharField(max_length=200,blank=False,null=False)

    def __str__(self):
        return self.trimestre