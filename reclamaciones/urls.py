from django.urls import path

from . import views

app_name = 'reclamaciones'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/<int:objeto_id>/', views.nueva, name='nueva'),
    path('<int:pk>/', views.revisar, name='revisar'),
    path('<int:pk>/aprobar/', views.aprobar, name='aprobar'),
    path('<int:pk>/rechazar/', views.rechazar, name='rechazar'),
]
