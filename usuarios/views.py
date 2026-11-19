from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import LoginForm, RegistroForm


class IniciarSesionView(LoginView):
    """Inicio de sesión con correo institucional (RF-01)."""
    template_name = 'usuarios/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


def registro(request):
    """Crear una cuenta con correo institucional (RF-01)."""
    if request.user.is_authenticated:
        return redirect('core:inicio')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, 'Tu cuenta se creó. ¡Bienvenido a Encuéntralo!')
            return redirect('core:inicio')
        messages.error(request, 'Revisa los campos marcados en rojo.')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})