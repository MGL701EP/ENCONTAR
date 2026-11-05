"""
Rutas principales del proyecto Encuéntralo.
Cada app tiene su propio archivo urls.py y aquí solo se incluyen.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('objetos/', include('objetos.urls')),
    path('usuarios/', include('usuarios.urls')),
]