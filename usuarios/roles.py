"""Roles del sistema (RF-01, RF-11 y RF-12).

- Usuario de la comunidad: cualquier cuenta con correo institucional.
- Bienestar Universitario: usuarios del grupo «Bienestar» (o superusuarios).
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

GRUPO_BIENESTAR = 'Bienestar'


def es_bienestar(usuario):
    """True si el usuario pertenece a Bienestar Universitario."""
    if not usuario.is_authenticated:
        return False
    return usuario.is_superuser or usuario.groups.filter(name=GRUPO_BIENESTAR).exists()


def puede_gestionar(usuario, reporte):
    """RF-11 y RF-12: solo el autor del reporte o Bienestar pueden editarlo o eliminarlo."""
    if not usuario.is_authenticated:
        return False
    return reporte.autor_id == usuario.id or es_bienestar(usuario)


def solo_bienestar(vista):
    """Decorador: la vista solo la puede usar Bienestar Universitario."""
    @login_required
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not es_bienestar(request.user):
            raise PermissionDenied('Solo Bienestar Universitario puede hacer esto.')
        return vista(request, *args, **kwargs)
    return envoltura