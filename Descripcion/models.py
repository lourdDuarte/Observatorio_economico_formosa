from django.db import models

# Create your models here.
class Descripcion(models.Model):
    nombre_modelo = models.CharField(max_length=200, null=False, blank=False)
    descripcion = models.TextField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
                return str(self.nombre_modelo)