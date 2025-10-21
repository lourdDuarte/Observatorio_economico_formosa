from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Descripcion)
class IndicadoresAdmin(admin.ModelAdmin):
    list_display = ['nombre_modelo']
   
    list_per_page = 15
