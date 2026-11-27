from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from objetos.models import EstadoReporte, Reporte
from usuarios.roles import solo_bienestar

from .forms import AprobarForm, RechazarForm, ReclamacionForm
from .models import EstadoReclamacion, Reclamacion


@login_required
def nueva(request, objeto_id):
    """El posible dueño reclama un objeto encontrado con la descripción a ciegas (RF-07)."""
    reporte = get_object_or_404(
        Reporte, pk=objeto_id, visible=True, tipo=Reporte.Tipo.ENCONTRADO,
    )
    if reporte.autor_id == request.user.id:
        raise PermissionDenied('No puedes reclamar un objeto que tú mismo reportaste.')
    if reporte.estado == EstadoReporte.DEVUELTO:
        messages.error(request, 'Este objeto ya fue devuelto a su dueño.')
        return redirect('objetos:detalle', objeto_id=reporte.pk)
    ya_reclamado = Reclamacion.objects.filter(
        reporte=reporte, reclamante=request.user, estado=EstadoReclamacion.PENDIENTE,
    ).exists()
    if ya_reclamado:
        messages.error(request, 'Ya tienes una reclamación en revisión para este objeto.')
        return redirect('objetos:detalle', objeto_id=reporte.pk)

    if request.method == 'POST':
        form = ReclamacionForm(request.POST, request.FILES, usuario=request.user)
        if form.is_valid():
            reclamacion = form.save(commit=False)
            reclamacion.reporte = reporte
            reclamacion.reclamante = request.user
            reclamacion.enviar()
            messages.success(
                request,
                'Tu reclamación quedó en revisión. Bienestar Universitario te avisará por correo.',
            )
            return redirect('objetos:detalle', objeto_id=reporte.pk)
        messages.error(request, 'Revisa los campos marcados en rojo.')
    else:
        form = ReclamacionForm(usuario=request.user)

    return render(request, 'reclamaciones/nueva.html', {'form': form, 'objeto': reporte})


@solo_bienestar
def lista(request):
    """Bandeja de Bienestar: reclamaciones por estado (RF-09). Por defecto, las pendientes."""
    estado = request.GET.get('estado', EstadoReclamacion.PENDIENTE)
    reclamaciones = Reclamacion.objects.select_related('reporte', 'reclamante')
    if estado in EstadoReclamacion.values:
        reclamaciones = reclamaciones.filter(estado=estado)
    else:
        estado = ''
    contexto = {
        'reclamaciones': reclamaciones,
        'estados': EstadoReclamacion.choices,
        'estado_actual': estado,
    }
    return render(request, 'reclamaciones/lista.html', contexto)


def _mostrar_revision(request, reclamacion, aprobar_form=None, rechazar_form=None):
    """Pantalla de revisión: descripción a ciegas frente a los rasgos registrados."""
    if aprobar_form is None:
        nombre = reclamacion.reclamante.get_full_name() or reclamacion.reclamante.username
        aprobar_form = AprobarForm(initial={'persona_recibe': nombre})
    contexto = {
        'reclamacion': reclamacion,
        'objeto': reclamacion.reporte,
        'aprobar_form': aprobar_form,
        'rechazar_form': rechazar_form or RechazarForm(),
    }
    return render(request, 'reclamaciones/revisar.html', contexto)


@solo_bienestar
def revisar(request, pk):
    """Bienestar compara la reclamación con el reporte antes de decidir (RF-09)."""
    reclamacion = get_object_or_404(
        Reclamacion.objects.select_related('reporte', 'reclamante', 'reporte_perdida'), pk=pk,
    )
    return _mostrar_revision(request, reclamacion)


def _reclamacion_pendiente(request, pk):
    """Devuelve la reclamación solo si sigue pendiente; si ya se decidió, devuelve None."""
    reclamacion = get_object_or_404(Reclamacion, pk=pk)
    if not reclamacion.esta_pendiente:
        messages.error(request, 'Esta reclamación ya fue revisada.')
        return None
    return reclamacion


@solo_bienestar
@require_POST
def aprobar(request, pk):
    """Bienestar aprueba y registra la entrega; el reporte pasa a Devuelto (RF-09)."""
    reclamacion = _reclamacion_pendiente(request, pk)
    if reclamacion is None:
        return redirect('reclamaciones:revisar', pk=pk)
    form = AprobarForm(request.POST)
    if form.is_valid():
        reclamacion.aprobar(
            persona_recibe=form.cleaned_data['persona_recibe'],
            prueba_fisica=form.cleaned_data['prueba_fisica'],
        )
        messages.success(request, 'Reclamación aprobada. La entrega quedó registrada.')
        return redirect('reclamaciones:lista')
    messages.error(request, 'Revisa los datos de la entrega.')
    return _mostrar_revision(request, reclamacion, aprobar_form=form)


@solo_bienestar
@require_POST
def rechazar(request, pk):
    """Bienestar rechaza con un motivo; el reporte sigue disponible (RF-09)."""
    reclamacion = _reclamacion_pendiente(request, pk)
    if reclamacion is None:
        return redirect('reclamaciones:revisar', pk=pk)
    form = RechazarForm(request.POST)
    if form.is_valid():
        reclamacion.rechazar(form.cleaned_data['motivo'])
        messages.success(request, 'Reclamación rechazada. Se guardó el motivo.')
        return redirect('reclamaciones:lista')
    messages.error(request, 'Escribe el motivo del rechazo.')
    return _mostrar_revision(request, reclamacion, rechazar_form=form)
