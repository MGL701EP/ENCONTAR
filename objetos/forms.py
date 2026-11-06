import re
from datetime import date

from django import forms

from .models import Reporte, Sede


class ReporteForm(forms.ModelForm):
    """Formulario para crear y editar reportes (RF-02, RF-03, RF-11)."""

    class Meta:
        model = Reporte
        fields = [
            'tipo', 'titulo', 'categoria', 'sede', 'lugar', 'fecha',
            'descripcion', 'foto_general', 'ubicacion_actual', 'rasgos_distintivos',
        ]
        widgets = {
            'tipo': forms.RadioSelect,
            'titulo': forms.TextInput(attrs={'placeholder': 'Ej.: Audífonos blancos con estuche'}),
            'lugar': forms.TextInput(attrs={'placeholder': 'Ej.: Bloque principal - piso 2'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'descripcion': forms.Textarea(attrs={
                'rows': 4, 'placeholder': 'Color, marca, detalles que ayuden a reconocerlo',
            }),
            'rasgos_distintivos': forms.Textarea(attrs={
                'rows': 3, 'placeholder': 'Marca, marcas particulares o contenido (no se muestran públicamente)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo dos botones de tipo: Perdí algo / Encontré algo (sin opción vacía)
        self.fields['tipo'].choices = Reporte.Tipo.choices
        # Texto en español para la opción vacía de las listas
        self.fields['categoria'].choices = [('', 'Selecciona…')] + list(Reporte.Categoria.choices)
        self.fields['sede'].choices = [('', 'Selecciona…')] + list(Sede.choices)
        self.fields['ubicacion_actual'].choices = [('', 'Selecciona…')] + list(Reporte.UbicacionActual.choices)
        # Clase CSS del diseño para todos los campos, menos los botones de tipo
        for nombre, campo in self.fields.items():
            if nombre != 'tipo':
                campo.widget.attrs['class'] = 'campo'
    # ---- Reglas de validación del servidor ----

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha > date.today():
            raise forms.ValidationError('La fecha no puede ser futura.')
        return fecha

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '')
        # RNF-01: no publicar números de celular en la descripción
        if re.search(r'(\d[\s.-]?){7,}', descripcion):
            raise forms.ValidationError(
                'No escribas números de teléfono. La plataforma se encarga del contacto.'
            )
        return descripcion

    def clean(self):
        datos = super().clean()
        if datos.get('tipo') == Reporte.Tipo.ENCONTRADO:
            # RF-03: un objeto encontrado siempre indica dónde está
            if not datos.get('ubicacion_actual'):
                self.add_error('ubicacion_actual', 'Indica dónde está el objeto ahora.')
        else:
            # Los campos de hallazgo no aplican a un objeto perdido
            datos['ubicacion_actual'] = ''
            datos['rasgos_distintivos'] = ''
        return datos