from django.urls import path

from . import views

app_name = 'objetos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('reportar/', views.reportar, name='reportar'),
    path('<int:objeto_id>/', views.detalle, name='detalle'),
]