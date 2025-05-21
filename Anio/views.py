from django.shortcuts import render
from .models import *

# Create your views here.

def all_year():
    anios = Anio.objects.all()

    return anios