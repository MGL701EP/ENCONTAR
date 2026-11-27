from django.apps import AppConfig


class ReclamacionesConfig(AppConfig):
    name = 'reclamaciones'

    def ready(self):
        # Conecta los avisos por correo (patrón Observador, RF-10)
        from . import signals  # noqa: F401
