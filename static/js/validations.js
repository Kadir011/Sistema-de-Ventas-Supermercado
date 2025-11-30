document.addEventListener('DOMContentLoaded', function() {
    // Seleccionamos todos los inputs marcados con 'only-numbers'
    const inputs = document.querySelectorAll('.only-numbers');

    inputs.forEach(input => {
        // 1. Evento INPUT: Reemplaza cualquier cosa que no sea número instantáneamente
        input.addEventListener('input', function() {
            // Si el valor contiene algo que no sea dígito, lo borra
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        // 2. Evento KEYPRESS: Bloquea la tecla antes de que se escriba
        input.addEventListener('keypress', function(e) {
            // Permitir teclas de control (borrar, flechas, etc) no es necesario filtrar aquí
            // porque keypress no se dispara para teclas especiales en todos los navegadores,
            // pero sí filtramos caracteres imprimibles.
            if (e.key && !/[0-9]/.test(e.key)) {
                e.preventDefault();
            }
        });

        // 3. Evento PASTE: Evita pegar texto que contenga letras
        input.addEventListener('paste', function(e) {
            // Obtener el texto que se intenta pegar
            const pasteData = (e.clipboardData || window.clipboardData).getData('text');
            // Si no son solo números, cancelamos el pegado
            if (!/^\d+$/.test(pasteData)) {
                e.preventDefault();
            }
        });
    });
});