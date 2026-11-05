from django.shortcuts import render


def iniciar_sesion(request):
    """Pantalla de inicio de sesión (la autenticación real llega en la Clase 3)."""
    return render(request, 'usuarios/login.html')