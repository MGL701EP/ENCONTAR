from django.shortcuts import render

from objetos.datos import OBJETOS


def inicio(request):
    """Página de inicio: presenta la plataforma y los últimos reportes."""
    contexto = {
        'recientes': OBJETOS[:4],
    }
    return render(request, 'core/inicio.html', contexto)