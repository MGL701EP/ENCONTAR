
from django.conf import settings
from django.db import models


class Sede(models.TextChoices):
    """Enumeración «Sede» del diagrama de clases."""
    BIBLIOTECA = 'biblioteca', 'Sede Biblioteca'
    RAFAEL_NUNEZ = 'rafael_nunez', 'Sede Rafael Núñez'


class EstadoReporte(models.TextChoices):
    """Enumeración «EstadoReporte» del diagrama de clases (RF-09)."""
    ABIERTO = 'abierto', 'Abierto'
    EN_CUSTODIA = 'en_custodia', 'En custodia'
    EN_RECLAMACION = 'en_reclamacion', 'En reclamación'
    DEVUELTO = 'devuelto', 'Devuelto'
    VENCIDO = 'vencido', 'Vencido'


class Reporte(models.Model):
    """Clase Reporte del diagrama de clases.

    En el diagrama, Reporte es abstracta y tiene dos hijas: ReportePerdida y
    ReporteHallazgo. Aquí se guardan en una sola tabla con el campo `tipo`;
    los atributos exclusivos de ReporteHallazgo (rasgos_distintivos y
    ubicacion_actual) quedan opcionales.
    """

    class Tipo(models.TextChoices):
        PERDIDO = 'perdido', 'Perdido'          # ReportePerdida
        ENCONTRADO = 'encontrado', 'Encontrado'  # ReporteHallazgo

    class Categoria(models.TextChoices):
        ELECTRONICA = 'electronica', 'Electrónica'
        LLAVES = 'llaves', 'Llaves'
        TERMOS = 'termos', 'Termos y botellas'
        ROPA = 'ropa', 'Ropa'
        DOCUMENTOS = 'documentos', 'Documentos y carnés'
        OTROS = 'otros', 'Otros'

    class UbicacionActual(models.TextChoices):
        QUIEN_ENCONTRO = 'quien_encontro', 'Lo tiene quien lo encontró'
        BIENESTAR = 'bienestar', 'Entregado en Bienestar Universitario'

    ICONOS = {
        'electronica': '🎧',
        'llaves': '🔑',
        'termos': '🧴',
        'ropa': '👕',
        'documentos': '🪪',
        'otros': '📦',
    }

    # Atributos de Reporte (diagrama de clases)
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    titulo = models.CharField('nombre del objeto', max_length=100)
    categoria = models.CharField('categoría', max_length=20, choices=Categoria.choices)
    descripcion = models.TextField('descripción', blank=True)
    sede = models.CharField(max_length=20, choices=Sede.choices)
    lugar = models.CharField(max_length=100)
    fecha = models.DateField('fecha de la pérdida o del hallazgo')
    foto_general = models.ImageField('foto general', upload_to='reportes/%Y/%m/', blank=True)
    estado = models.CharField(max_length=20, choices=EstadoReporte.choices, default=EstadoReporte.ABIERTO)
    visible = models.BooleanField(default=True, help_text='Bienestar puede ocultar un reporte (RF-12).')

    # Atributos de ReporteHallazgo
    rasgos_distintivos = models.TextField(
        'rasgos distintivos', blank=True,
        help_text='Marca, marcas particulares o contenido. Nunca se muestran públicamente (RF-03, RF-05).',
    )
    ubicacion_actual = models.CharField(
        'dónde está ahora', max_length=20, choices=UbicacionActual.choices, blank=True,
    )

    # Relación «Usuario 1 — publica — 0..* Reporte»
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reportes',
    )

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', '-creado']

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.titulo}'

    @property
    def es_encontrado(self):
        return self.tipo == self.Tipo.ENCONTRADO

    @property
    def icono(self):
        return self.ICONOS.get(self.categoria, '📦')

    # Métodos del diagrama de clases
    def cambiar_estado(self, estado):
        self.estado = estado
        self.save(update_fields=['estado', 'actualizado'])

    def marcar_resuelto(self):
        self.cambiar_estado(EstadoReporte.DEVUELTO)

    def ocultar(self):
        self.visible = False
        self.save(update_fields=['visible', 'actualizado'])

    def obtener_detalle_publico(self):
        """Datos que se pueden mostrar a cualquiera: nunca incluye los rasgos distintivos (RF-05)."""
        return {
            'titulo': self.titulo,
            'tipo': self.get_tipo_display(),
            'categoria': self.get_categoria_display(),
            'sede': self.get_sede_display(),
            'lugar': self.lugar,
            'fecha': self.fecha,
            'estado': self.get_estado_display(),
            'ubicacion_actual': self.get_ubicacion_actual_display(),
        }