from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from .datos import (
    CATEGORIAS,
    LUGARES,
    OBJETOS,
    PUNTOS_ENTREGA,
    buscar_objeto,
    nombre_categoria,
)


def lista(request):
    """Listado de objetos con filtros por texto, tipo y categoría."""
    texto = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    categoria = request.GET.get('categoria', '')

    resultados = OBJETOS
    if texto:
        t = texto.lower()
        resultados = [
            o for o in resultados
            if t in o['titulo'].lower() or t in o['descripcion'].lower() or t in o['lugar'].lower()
        ]
    if tipo:
        resultados = [o for o in resultados if o['tipo'] == tipo]
    if categoria:
        resultados = [o for o in resultados if o['categoria'] == categoria]

    contexto = {
        'objetos': resultados,
        'categorias': CATEGORIAS,
        'filtros': {'q': texto, 'tipo': tipo, 'categoria': categoria},
    }
    return render(request, 'objetos/lista.html', contexto)


def detalle(request, objeto_id):
    """Detalle de un objeto reportado."""
    objeto = buscar_objeto(objeto_id)
    if objeto is None:
        raise Http404('Objeto no encontrado')

    contexto = {
        'objeto': objeto,
        'categoria': nombre_categoria(objeto['categoria']),
    }
    return render(request, 'objetos/detalle.html', contexto)


def reportar(request):
    """Formulario para reportar un objeto perdido o encontrado.
    En esta primera entrega el reporte todavía no se guarda.
    """
    if request.method == 'POST':
        messages.success(
            request,
            'Reporte recibido. (Versión de prueba: aún no se guarda en la base de datos.)',
        )
        return redirect('objetos:lista')

    contexto = {
        'categorias': CATEGORIAS,
        'lugares': LUGARES,
        'puntos_entrega': PUNTOS_ENTREGA,
        'tipo_inicial': request.GET.get('tipo', 'perdido'),
    }
    return render(request, 'objetos/reportar.html', contexto)