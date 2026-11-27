from usuarios.roles import es_bienestar

from .models import EstadoReclamacion, Reclamacion


def pendientes(request):
    """Contador del menú «Reclamaciones»: solo se calcula para Bienestar."""
    if not es_bienestar(request.user):
        return {}
    total = Reclamacion.objects.filter(estado=EstadoReclamacion.PENDIENTE).count()
    return {'reclamaciones_pendientes': total}
