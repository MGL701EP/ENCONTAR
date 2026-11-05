// Encuéntralo · Interacciones básicas del frontend

document.addEventListener('DOMContentLoaded', () => {
    // 1. Menú desplegable en celulares
    const boton = document.querySelector('[data-menu-boton]');
    const menu = document.querySelector('[data-menu]');
    if (boton && menu) {
        boton.addEventListener('click', () => {
            const abierto = menu.classList.toggle('abierto');
            boton.setAttribute('aria-expanded', abierto);
        });
    }

    // 2. En el formulario de reporte, mostrar "¿Dónde lo dejaste?" solo si se encontró el objeto
    const campoEntrega = document.querySelector('[data-solo-encontrado]');
    const radiosTipo = document.querySelectorAll('input[name="tipo"]');
    if (campoEntrega && radiosTipo.length) {
        const actualizar = () => {
            const tipo = document.querySelector('input[name="tipo"]:checked').value;
            campoEntrega.classList.toggle('oculto', tipo !== 'encontrado');
        };
        radiosTipo.forEach((radio) => radio.addEventListener('change', actualizar));
        actualizar();
    }

    // 3. Botón de contacto en el detalle (se implementa en una próxima entrega)
    const contactar = document.querySelector('[data-contactar]');
    if (contactar) {
        contactar.addEventListener('click', () => {
            alert('Pronto podrás contactar a la otra persona de forma privada desde aquí.');
        });
    }
});