"""Avisos por correo de las reclamaciones (RF-10).

Patrón Observador: estas funciones «escuchan» cuando se guarda una
reclamación y avisan a los interesados, sin que las vistas tengan que
saber a quién notificar. En desarrollo los correos salen en la terminal.
"""
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from usuarios.roles import GRUPO_BIENESTAR

from .models import EstadoReclamacion, Reclamacion


def _correos_bienestar():
    Usuario = get_user_model()
    usuarios = Usuario.objects.filter(
        Q(groups__name=GRUPO_BIENESTAR) | Q(is_superuser=True), is_active=True,
    ).exclude(email='')
    return list(usuarios.values_list('email', flat=True).distinct())


def _avisar(asunto, mensaje, destinatarios):
    """Envía el correo solo cuando la operación se guardó por completo en la base de datos."""
    destinatarios = [correo for correo in destinatarios if correo]
    if not destinatarios:
        return
    transaction.on_commit(lambda: send_mail(
        f'Encuéntralo: {asunto}', mensaje, None, destinatarios, fail_silently=True,
    ))


@receiver(pre_save, sender=Reclamacion)
def recordar_estado_anterior(sender, instance, **kwargs):
    """Guarda el estado previo para saber si cambió al guardar."""
    anterior = None
    if instance.pk:
        anterior = Reclamacion.objects.filter(pk=instance.pk).values_list('estado', flat=True).first()
    instance._estado_anterior = anterior


@receiver(post_save, sender=Reclamacion)
def avisar_cambios(sender, instance, created, **kwargs):
    reporte = instance.reporte

    # Nueva reclamación: avisar a Bienestar (secuencia, mensajes 14 y 15)
    if created:
        _avisar(
            'nueva reclamación pendiente',
            f'Hay una nueva reclamación para "{reporte.titulo}" ({reporte.get_sede_display()}).\n'
            'Ingresa a la plataforma, en el menú Reclamaciones, para revisarla.',
            _correos_bienestar(),
        )
        return

    if instance._estado_anterior == instance.estado:
        return

    reclamante = instance.reclamante
    if instance.estado == EstadoReclamacion.APROBADA:
        _avisar(
            'tu reclamación fue aprobada',
            f'Tu reclamación de "{reporte.titulo}" fue aprobada y la entrega quedó registrada.',
            [reclamante.email],
        )
        # Diagrama de actividades: se avisa a quien encontró el objeto
        if reporte.autor and reporte.autor_id != reclamante.id:
            _avisar(
                'el objeto que encontraste fue devuelto',
                f'El objeto "{reporte.titulo}" que reportaste ya fue entregado a su dueño. Gracias por ayudar.',
                [reporte.autor.email],
            )
    elif instance.estado == EstadoReclamacion.RECHAZADA:
        _avisar(
            'tu reclamación fue rechazada',
            f'Tu reclamación de "{reporte.titulo}" fue rechazada.\n'
            f'Motivo: {instance.motivo_rechazo}',
            [reclamante.email],
        )
