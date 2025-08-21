"""observatorioeconomico URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from observatorioeconomico import utils as utils
from django.conf.urls.static import static

from observatorioeconomico import views as observatorio
from Supermercado import views as supermercado
from Patentamiento import views as vehiculo
from Ipc import views as ipc
from Transferencia import views as transferencia
from Sector_construccion import views as construccion
from sector_privado import views as privado
from Dgr import views as dgr

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', observatorio.index, name='index'),
    path('precio-corriente/', supermercado.view_precio_corriente, name='precio-corriente'),
    path('precio-constante/', supermercado.view_precio_constante, name='precio-constante'),
    path('patentamiento-auto/', vehiculo.view_patentamiento_auto, name='patentamiento-auto'),
    path('patentamiento-moto/', vehiculo.view_patentamiento_moto, name='patentamiento-moto'),
    path('transferencia-auto/', vehiculo.view_transferencia_auto, name='transferencia-auto'),
    path('transferencia-moto/', vehiculo.view_transferencia_moto, name='transferencia-moto'),
    path('transferencias/', transferencia.view_transferencia, name='transferencias'),
    path('ipc/', ipc.ipc, name='ipc'),
    path('salario-construccion/', construccion.view_construccion_salarios, name='salario-construccion'),
    path('puestos-construccion/', construccion.view_construccion_puestos, name='puestos-construccion'),
    path('sector-privado/', privado.view_sector_privado, name='sector-privado'),
    path('sector-privado-ramas/', privado.view_sector_privado_ramas, name='sector-privado-ramas'),
    path('recaudacion/', dgr.view_recaudacion, name='recaudacion'),
    path('variables/', utils.process_data_consult, name='variables'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
