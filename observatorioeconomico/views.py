from django.shortcuts import render, redirect
import requests

def index(request):
    
    URL = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias"
    response = requests.get(URL, verify=False)
    
    if response.status_code == 200:
       
        data = response.json()
        print(data)
    return render (request, 'index.html')