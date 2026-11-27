from django.contrib import admin

from .models import Entrega, Reclamacion


class EntregaInline(admin.StackedInline):
    model = Entrega
    extra = 0
    readonly_fields = ('fecha',)


@admin.register(Reclamacion)
class ReclamacionAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'reclamante', 'fecha', 'estado')
    list_filter = ('estado',)
    search_fields = ('reporte__titulo', 'reclamante__username', 'descripcion_ciegas')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)
    inlines = [EntregaInline]


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('reclamacion', 'persona_recibe', 'prueba_fisica', 'fecha')
    list_filter = ('prueba_fisica',)
    readonly_fields = ('fecha',)
