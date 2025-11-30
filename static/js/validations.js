document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar inputs por la clase 'only-numbers'
    const inputs = document.querySelectorAll('.only-numbers');

    inputs.forEach(input => {
        // Función para aplicar los colores del "Semáforo"
        const updateInputState = () => {
            // Obtener el límite del atributo maxlength HTML
            const max = parseInt(input.getAttribute('maxlength'));
            const currentLength = input.value.length;

            // Limpiar todas las clases de borde de estado
            input.classList.remove('border-gray-300', 'border-red-500', 'border-green-500', 'border-yellow-500', 'focus:ring-green-500', 'focus:border-green-500');
            
            // Añadir borde base para que se note el color
            input.classList.add('border-2', 'focus:outline-none'); 

            if (currentLength === 0) {
                // Estado: Vacío (Gris por defecto o Azul al foco)
                input.classList.add('border-gray-300', 'focus:border-blue-500');
            } else if (currentLength < max) {
                // Estado: Escribiendo incompleto (Amarillo)
                input.classList.add('border-yellow-500');
            } else if (currentLength === max) {
                // Estado: Completo (Verde)
                input.classList.add('border-green-500');
            }
        };

        // Evento principal: INPUT
        input.addEventListener('input', function() {
            const max = parseInt(this.getAttribute('maxlength'));

            // 1. Eliminar cualquier caracter que no sea número
            this.value = this.value.replace(/[^0-9]/g, '');

            // 2. FORZAR el límite: Si se pasa (ej: pegar texto largo), lo corta
            if (this.value.length > max) {
                this.value = this.value.slice(0, max);
            }

            // 3. Actualizar colores
            updateInputState();
        });

        // Inicializar estado al cargar la página (por si hay datos guardados)
        updateInputState();
    });

    // Validación al enviar el formulario (Submit)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let hasError = false;
            const formInputs = form.querySelectorAll('.only-numbers');

            formInputs.forEach(input => {
                const max = parseInt(input.getAttribute('maxlength'));
                // Si tiene datos pero no está completo
                if (input.value.length > 0 && input.value.length < max) {
                    e.preventDefault(); // Bloquear envío
                    
                    // Estado: Error (Rojo)
                    input.classList.remove('border-yellow-500', 'border-green-500', 'border-gray-300');
                    input.classList.add('border-2', 'border-red-500');
                    hasError = true;
                }
            });

            if (hasError) {
                alert('Por favor, completa los dígitos requeridos en los campos marcados en rojo.');
            }
        });
    });
});