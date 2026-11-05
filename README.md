# Encuéntralo

Plataforma web para reportar y recuperar objetos perdidos en la Corporación Universitaria Rafael Núñez (Sede Biblioteca y Sede Rafael Núñez).

**Proyecto integrador · Aplicaciones Web II**
**Grupo:** MJ INDUSTRIES

## Integrantes

- Jesús Vergara
- Miguel Estrada

## Problema

Cuando alguien pierde una pertenencia en la universidad (carné, USB, calculadora, termo, llaves, etc.) no existe un canal claro para buscarla: se pregunta a conocidos, se revisan grupos de WhatsApp o se va a vigilancia sin saber si allí la entregaron. Quien encuentra un objeto tampoco sabe a quién entregarlo. Encuéntralo reúne en un solo lugar los reportes de objetos perdidos y encontrados, sin exponer los datos personales de los estudiantes.

## Tecnologías

- Python 3 y Django
- HTML, CSS y JavaScript
- SQLite en desarrollo (MySQL en la siguiente entrega)

## Pantallas (Clase 1)

| Pantalla | Ruta |
|---|---|
| Inicio | `/` |
| Listado de objetos con filtros | `/objetos/` |
| Detalle de un objeto | `/objetos/<id>/` |
| Reportar objeto | `/objetos/reportar/` |
| Iniciar sesión | `/usuarios/login/` |

## Cómo ejecutar el proyecto

```bash
git clone https://github.com/MGL701EP/ENCONTAR.git
cd ENCONTAR
python -m venv venv
venv\Scripts\activate        # En Mac o Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Luego abrir http://127.0.0.1:8000 en el navegador.

## Estructura

```
encuentralo/   Configuración del proyecto (settings y URLs principales)
core/          Página de inicio
objetos/       Listado, detalle y reporte de objetos
usuarios/      Inicio de sesión
templates/     Plantillas HTML (base.html y pantallas)
static/        CSS, JavaScript e imágenes
```