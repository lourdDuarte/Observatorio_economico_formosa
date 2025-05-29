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
from observatorioeconomico import utils 
from django.conf.urls.static import static

from observatorioeconomico import views as observatorio
from Supermercado import views as supermercado
from Patentamiento import views as vehiculo

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', observatorio.index, name='index'),
    path('api/chart/<str:model_name>/<int:anio_id>/<int:valor_id>/', utils.get_api_chart_view, name='get_chart_data'),
    path('precio-corriente/', supermercado.view_precio_corriente, name='precio-corriente'),
    path('precio-constante/', supermercado.view_precio_constante, name='precio-constante'),
    path('patentamiento-auto/', vehiculo.view_patentamiento_auto, name='patentamiento-auto'),
    path('transferencia-auto/', vehiculo.view_transferencia_auto, name='transferencia-auto'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
