"""
Datos de ejemplo para las primeras pantallas (Clase 1).
En la Clase 2 esta lista se reemplaza por el modelo Objeto conectado a MySQL.
"""

CATEGORIAS = [
    ('electronica', 'Electrónica'),
    ('llaves', 'Llaves'),
    ('termos', 'Termos y botellas'),
    ('ropa', 'Ropa'),
    ('documentos', 'Documentos y carnés'),
    ('otros', 'Otros'),
]

LUGARES = [
    'Bloque principal - piso 2',
    'Bloque principal - piso 4',
    'Lockers',
    'Zonas comunes',
    'Portería',
]

PUNTOS_ENTREGA = [
    'Bienestar Universitario',
    'Portería',
    'Lo tiene quien lo encontró',
]

OBJETOS = [
    {
        'id': 1,
        'titulo': 'Audífonos inalámbricos sin estuche',
        'tipo': 'encontrado',
        'categoria': 'electronica',
        'icono': '🎧',
        'lugar': 'Bloque principal - piso 4',
        'fecha': '2026-10-20',
        'descripcion': 'Audífonos blancos encontrados en un salón del cuarto piso. No tienen estuche.',
        'punto_entrega': 'Lo tiene quien lo encontró',
    },
    {
        'id': 2,
        'titulo': 'Llave con llavero decorativo',
        'tipo': 'encontrado',
        'categoria': 'llaves',
        'icono': '🔑',
        'lugar': 'Zonas comunes',
        'fecha': '2026-10-21',
        'descripcion': 'Una llave sola con un llavero de colores. Se encontró en el pasillo.',
        'punto_entrega': 'Lo tiene quien lo encontró',
    },
    {
        'id': 3,
        'titulo': 'Audífonos con estuche',
        'tipo': 'encontrado',
        'categoria': 'electronica',
        'icono': '🎧',
        'lugar': 'Lockers',
        'fecha': '2026-10-22',
        'descripcion': 'Audífonos con su estuche, encontrados sobre los lockers del segundo piso.',
        'punto_entrega': 'Bienestar Universitario',
    },
        {
        'id': 4,
        'titulo': 'Calculadora científica Casio',
        'tipo': 'perdido',
        'categoria': 'electronica',
        'icono': '🧮',
        'lugar': 'Bloque principal - piso 2',
        'fecha': '2026-10-23',
        'descripcion': 'Calculadora científica Casio gris, perdida después de clase en el segundo piso. Tiene un sticker en la tapa.',
        'punto_entrega': '',
    },
]


def nombre_categoria(clave):
    """Devuelve el nombre legible de una categoría."""
    return dict(CATEGORIAS).get(clave, 'Otros')


def buscar_objeto(objeto_id):
    """Devuelve el objeto con ese id, o None si no existe."""
    for objeto in OBJETOS:
        if objeto['id'] == objeto_id:
            return objeto
    return None