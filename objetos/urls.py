from django.urls import path

from . import views

app_name = 'objetos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('reportar/', views.reportar, name='reportar'),
    path('mis-reportes/', views.mis_reportes, name='mis_reportes'),
    path('<int:objeto_id>/', views.detalle, name='detalle'),
    path('<int:objeto_id>/editar/', views.editar, name='editar'),
    path('<int:objeto_id>/eliminar/', views.eliminar, name='eliminar'),
    path('<int:objeto_id>/resuelto/', views.marcar_resuelto, name='resuelto'),
]