from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


def _dominio():
    return getattr(settings, 'DOMINIO_INSTITUCIONAL', '@campusuninunez.edu.co')


class LoginForm(AuthenticationForm):
    """Inicio de sesión con el correo institucional (RF-01)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Correo institucional'
        self.fields['username'].widget.attrs.update({
            'class': 'campo', 'placeholder': f'usuario{_dominio()}', 'autocomplete': 'username',
        })
        self.fields['password'].label = 'Contraseña'
        self.fields['password'].widget.attrs.update({'class': 'campo', 'placeholder': 'Tu contraseña'})

    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()


class RegistroForm(UserCreationForm):
    """Registro solo con correo institucional (RF-01): el correo es el nombre de usuario."""

    email = forms.EmailField(label='Correo institucional')

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'placeholder': f'usuario{_dominio()}', 'autocomplete': 'email',
        })
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'campo'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if not email.endswith(_dominio()):
            raise forms.ValidationError(f'Usa tu correo institucional (debe terminar en {_dominio()}).')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['email']
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
        return usuario