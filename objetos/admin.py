from django.contrib import admin

from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'categoria', 'sede', 'lugar', 'fecha', 'estado', 'visible')
    list_filter = ('tipo', 'categoria', 'sede', 'estado', 'visible')
    search_fields = ('titulo', 'descripcion', 'lugar')
    date_hierarchy = 'fecha'