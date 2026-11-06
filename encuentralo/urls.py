"""
Rutas principales del proyecto Encuéntralo.
Cada app tiene su propio archivo urls.py y aquí solo se incluyen.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('objetos/', include('objetos.urls')),
    path('usuarios/', include('usuarios.urls')),
]

# En desarrollo, Django sirve las fotos subidas por los usuarios
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)