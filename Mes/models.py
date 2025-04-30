from django.db import models



# Create your models here.



class Mes(models.Model):
    mes = models.CharField(max_length=200,blank=False,null=False)

    def __str__(self):
        return self.mes