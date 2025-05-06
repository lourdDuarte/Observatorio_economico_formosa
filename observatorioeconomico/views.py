from django.shortcuts import render, redirect
import requests
from collections import defaultdict
import json
def index(request):
    
    URL = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias"
    response = requests.get(URL, verify=False)
    
    filter_api = [1,29,31,32,40,144,146]
    data_api = defaultdict(lambda: {'valor': [], 'fecha': []})
    if response.status_code == 200:
       
        data = response.json()
        for key in data['results']:
            if key['idVariable'] in filter_api:
                descripcion = key['descripcion']
                valor = key['valor']
                fecha = key['fecha']
                if key['idVariable'] == 29 or key['idVariable'] == 146 or key['idVariable'] == 144 :
                    data_api[descripcion]['valor'].append(str(valor) + '%')
                    data_api[descripcion]['fecha'].append(fecha)
                else:
                    data_api[descripcion]['valor'].append(valor)
                    data_api[descripcion]['fecha'].append(fecha)
                    
                
        
        data_combinada = {
            descripcion: list(zip(info['fecha'], info['valor']))
            for descripcion, info in data_api.items()
        }

        context = {
            'data_combinada': data_combinada
        }
        
    return render (request, 'index.html', context)

