from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from usuarios.roles import puede_gestionar

from .forms import ReporteForm
from .models import Reporte, Sede


def lista(request):
    """Listado de reportes guardados en MySQL, con búsqueda y filtros (RF-04)."""
    texto = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    categoria = request.GET.get('categoria', '')
    sede = request.GET.get('sede', '')

    reportes = Reporte.objects.filter(visible=True)
    if texto:
        reportes = reportes.filter(
            Q(titulo__icontains=texto) | Q(descripcion__icontains=texto) | Q(lugar__icontains=texto)
        )
    if tipo:
        reportes = reportes.filter(tipo=tipo)
    if categoria:
        reportes = reportes.filter(categoria=categoria)
    if sede:
        reportes = reportes.filter(sede=sede)

    contexto = {
        'objetos': reportes,
        'categorias': Reporte.Categoria.choices,
        'sedes': Sede.choices,
        'filtros': {'q': texto, 'tipo': tipo, 'categoria': categoria, 'sede': sede},
    }
    return render(request, 'objetos/lista.html', contexto)


def detalle(request, objeto_id):
    """Detalle de un reporte. Si no existe o está oculto, muestra error 404."""
    objeto = get_object_or_404(Reporte, pk=objeto_id, visible=True)
    contexto = {
        'objeto': objeto,
        # RF-11: solo el autor o Bienestar ven los botones de editar, resolver y eliminar
        'puede_gestionar': puede_gestionar(request.user, objeto),
    }
    return render(request, 'objetos/detalle.html', contexto)


@login_required
def reportar(request):
    """CREAR: guarda un nuevo reporte en MySQL (RF-02 y RF-03). Requiere sesión iniciada."""
    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.autor = request.user
            reporte.save()
            messages.success(request, 'Tu reporte se publicó correctamente.')
            return redirect('objetos:detalle', objeto_id=reporte.pk)
        messages.error(request, 'Revisa los campos marcados en rojo.')
    else:
        form = ReporteForm(initial={'tipo': request.GET.get('tipo', 'perdido')})

    return render(request, 'objetos/reportar.html', {'form': form})


def _reporte_gestionable(request, objeto_id):
    """RF-11: devuelve el reporte solo si el usuario es su autor o es Bienestar; si no, error 403."""
    objeto = get_object_or_404(Reporte, pk=objeto_id)
    if not puede_gestionar(request.user, objeto):
        raise PermissionDenied('Solo el autor del reporte o Bienestar pueden hacer esto.')
    return objeto


@login_required
def editar(request, objeto_id):
    """ACTUALIZAR: modifica un reporte existente (RF-11)."""
    objeto = _reporte_gestionable(request, objeto_id)
    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES, instance=objeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los cambios se guardaron correctamente.')
            return redirect('objetos:detalle', objeto_id=objeto.pk)
        messages.error(request, 'Revisa los campos marcados en rojo.')
    else:
        form = ReporteForm(instance=objeto)

    return render(request, 'objetos/reportar.html', {'form': form, 'objeto': objeto})


@login_required
def eliminar(request, objeto_id):
    """ELIMINAR: pide confirmación antes de borrar el reporte (RF-11)."""
    objeto = _reporte_gestionable(request, objeto_id)
    if request.method == 'POST':
        titulo = objeto.titulo
        objeto.delete()
        messages.success(request, f'El reporte "{titulo}" se eliminó.')
        return redirect('objetos:mis_reportes')

    return render(request, 'objetos/confirmar_eliminar.html', {'objeto': objeto})


@login_required
@require_POST
def marcar_resuelto(request, objeto_id):
    """RF-11: el autor (o Bienestar) marca el reporte como resuelto."""
    objeto = _reporte_gestionable(request, objeto_id)
    objeto.marcar_resuelto()
    messages.success(request, 'El reporte quedó marcado como resuelto.')
    return redirect('objetos:detalle', objeto_id=objeto.pk)


@login_required
def mis_reportes(request):
    """Reportes publicados por el usuario que inició sesión (RF-11)."""
    reportes = Reporte.objects.filter(autor=request.user).order_by('-creado')
    return render(request, 'objetos/mis_reportes.html', {'objetos': reportes})