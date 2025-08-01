document.addEventListener('DOMContentLoaded', () => {
    const stock = document.getElementById('id_stock');
    const state = document.getElementById('id_state');  

    // Función para actualizar el estado basado en el stock
    const updateState = () => {
        if (stock.value <= 0) {
            state.value = 'Agotado'; // El campo 'estado' se asigna como 'false' si el stock es 0
        }
        state.value = 'Disponible';  // El campo 'estado' se asigna como 'true' si el stock es mayor que 0
    };

    // Llamar a la función al cargar la página (en caso de edición)
    updateState();

    // Escuchar el evento 'input' en el campo de stock
    stock.addEventListener('input', updateState);
});

