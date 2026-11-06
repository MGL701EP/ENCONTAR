from django.shortcuts import render

from objetos.models import Reporte


def inicio(request):
    """Página de inicio: presenta la plataforma y los 4 reportes más recientes."""
    recientes = Reporte.objects.filter(visible=True).order_by('-creado')[:4]
    return render(request, 'core/inicio.html', {'recientes': recientes})