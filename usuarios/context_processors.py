from .roles import es_bienestar


def roles(request):
    """Disponible en todas las plantillas como {{ es_bienestar }}."""
    return {'es_bienestar': es_bienestar(request.user)}