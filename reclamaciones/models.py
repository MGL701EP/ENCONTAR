from django.conf import settings
from django.db import models, transaction

from objetos.models import EstadoReporte, Reporte


class EstadoReclamacion(models.TextChoices):
    """Enumeración «EstadoReclamacion» del diagrama de clases (RF-07, RF-09)."""
    PENDIENTE = 'pendiente', 'Pendiente'
    APROBADA = 'aprobada', 'Aprobada'
    RECHAZADA = 'rechazada', 'Rechazada'


class Reclamacion(models.Model):
    """Clase Reclamacion del diagrama de clases.

    Solicitud del posible dueño de un objeto encontrado. La descripción a
    ciegas se compara con los rasgos distintivos del reporte, que el
    reclamante nunca ve (RF-05, RF-07).
    """

    # Relación «ReporteHallazgo 1 — recibe — 0..* Reclamacion»
    reporte = models.ForeignKey(
        Reporte, on_delete=models.CASCADE, related_name='reclamaciones',
        limit_choices_to={'tipo': Reporte.Tipo.ENCONTRADO},
    )
    reclamante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reclamaciones',
    )
    descripcion_ciegas = models.TextField(
        'descripción a ciegas',
        help_text='Describe el objeto sin haber visto sus rasgos: marca, color, marcas, contenido.',
    )
    # Opcional: el reporte de pérdida que publicó el reclamante (cruce de reportes)
    reporte_perdida = models.ForeignKey(
        Reporte, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reclamaciones_vinculadas',
        limit_choices_to={'tipo': Reporte.Tipo.PERDIDO},
        verbose_name='mi reporte de pérdida',
    )
    foto_previa = models.ImageField(
        'foto previa del objeto', upload_to='reclamaciones/%Y/%m/', blank=True,
        help_text='Una foto tuya con el objeto, tomada antes de perderlo (opcional).',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=12, choices=EstadoReclamacion.choices, default=EstadoReclamacion.PENDIENTE,
    )
    motivo_rechazo = models.TextField('motivo del rechazo', blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'reclamación'
        verbose_name_plural = 'reclamaciones'

    def __str__(self):
        return f'Reclamación de {self.reporte.titulo} ({self.get_estado_display()})'

    @property
    def esta_pendiente(self):
        return self.estado == EstadoReclamacion.PENDIENTE

    # Métodos del diagrama de clases
    def enviar(self):
        """Guarda la reclamación como Pendiente y el reporte pasa a En reclamación (RF-07)."""
        with transaction.atomic():
            self.estado = EstadoReclamacion.PENDIENTE
            self.save()
            self.reporte.cambiar_estado(EstadoReporte.EN_RECLAMACION)

    def aprobar(self, persona_recibe, prueba_fisica=False):
        """Bienestar aprueba, registra la entrega y el reporte (y su pérdida vinculada) pasa a Devuelto (RF-09)."""
        with transaction.atomic():
            self.estado = EstadoReclamacion.APROBADA
            self.save(update_fields=['estado'])
            entrega = Entrega.objects.create(
                reclamacion=self, persona_recibe=persona_recibe, prueba_fisica=prueba_fisica,
            )
            self.reporte.marcar_resuelto()
            # Si vinculó su reporte de pérdida, ese caso también queda resuelto
            if self.reporte_perdida and self.reporte_perdida.estado != EstadoReporte.DEVUELTO:
                self.reporte_perdida.marcar_resuelto()
        return entrega

    def rechazar(self, motivo):
        """Bienestar rechaza con un motivo; el reporte sigue disponible (RF-09)."""
        with transaction.atomic():
            self.estado = EstadoReclamacion.RECHAZADA
            self.motivo_rechazo = motivo
            self.save(update_fields=['estado', 'motivo_rechazo'])
            hay_otras = self.reporte.reclamaciones.filter(
                estado=EstadoReclamacion.PENDIENTE,
            ).exists()
            if not hay_otras:
                if self.reporte.ubicacion_actual == Reporte.UbicacionActual.BIENESTAR:
                    self.reporte.cambiar_estado(EstadoReporte.EN_CUSTODIA)
                else:
                    self.reporte.cambiar_estado(EstadoReporte.ABIERTO)


class Entrega(models.Model):
    """Clase Entrega del diagrama de clases: cierre del caso (RF-09).

    Relación «Reclamacion 1 — genera — 0..1 Entrega».
    """

    reclamacion = models.OneToOneField(
        Reclamacion, on_delete=models.CASCADE, related_name='entrega',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    persona_recibe = models.CharField('persona que recibe', max_length=120)
    prueba_fisica = models.BooleanField(
        'se hizo prueba física', default=False,
        help_text='Por ejemplo, desbloquear el celular o conectar los audífonos.',
    )

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Entrega de {self.reclamacion.reporte.titulo}'
