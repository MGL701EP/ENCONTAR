from django import forms

from objetos.models import Reporte

from .models import Entrega, Reclamacion

MINIMO_DESCRIPCION = 20


class ReclamacionForm(forms.ModelForm):
    """Formulario para reclamar un objeto encontrado (RF-07)."""

    class Meta:
        model = Reclamacion
        fields = ['descripcion_ciegas', 'reporte_perdida', 'foto_previa']
        widgets = {
            'descripcion_ciegas': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Ej.: Audífonos marca X, el estuche tiene un rayón en la tapa y un sticker azul',
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo puede vincular sus propios reportes de pérdida
        perdidas = Reporte.objects.none()
        if usuario is not None and usuario.is_authenticated:
            perdidas = Reporte.objects.filter(autor=usuario, tipo=Reporte.Tipo.PERDIDO)
        self.fields['reporte_perdida'].queryset = perdidas
        self.fields['reporte_perdida'].empty_label = 'No tengo reporte de pérdida'
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'campo'

    def clean_descripcion_ciegas(self):
        descripcion = self.cleaned_data.get('descripcion_ciegas', '').strip()
        # Criterio de aceptación de RF-07: sin descripción a ciegas no hay reclamación
        if len(descripcion) < MINIMO_DESCRIPCION:
            raise forms.ValidationError(
                f'Describe el objeto con al menos {MINIMO_DESCRIPCION} caracteres '
                '(marca, color, marcas particulares o contenido).'
            )
        return descripcion


class AprobarForm(forms.ModelForm):
    """Bienestar aprueba la reclamación y registra la entrega (RF-09)."""

    class Meta:
        model = Entrega
        fields = ['persona_recibe', 'prueba_fisica']
        widgets = {
            'persona_recibe': forms.TextInput(attrs={'placeholder': 'Nombre de quien recibe el objeto'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['persona_recibe'].widget.attrs['class'] = 'campo'


class RechazarForm(forms.Form):
    """Bienestar rechaza la reclamación indicando el motivo (RF-09)."""

    motivo = forms.CharField(
        label='Motivo del rechazo',
        widget=forms.Textarea(attrs={
            'rows': 3, 'class': 'campo',
            'placeholder': 'Ej.: La descripción no coincide con los rasgos registrados',
        }),
    )

    def clean_motivo(self):
        motivo = self.cleaned_data['motivo'].strip()
        if not motivo:
            raise forms.ValidationError('Escribe el motivo del rechazo.')
        return motivo
