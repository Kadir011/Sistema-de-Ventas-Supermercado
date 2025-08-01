document.addEventListener('DOMContentLoaded', () => {
    const production_date = document.getElementById('id_production_date');
    const expiration_date = document.getElementById('id_expiration_date');

    // Función para calcular la fecha de vencimiento
    const calculateExpirationDate = () => {
        const prod_date = new Date(production_date.value);

        if (isNaN(prod_date)) {
            expiration_date.value = ''; // Limpiar si no hay fecha válida
        } 
        // Crear una nueva fecha con UTC para evitar problemas de huso horario
        const exp_date = new Date(Date.UTC(prod_date.getFullYear(), prod_date.getMonth(), prod_date.getDate()));
        exp_date.setUTCDate(exp_date.getUTCDate() + 30); // Sumar 30 días (o la cantidad que desees)

        // Convertir la fecha al formato yyyy-mm-dd
        const year = exp_date.getUTCFullYear();
        const month = String(exp_date.getUTCMonth() + 1).padStart(2, '0'); // Los meses van de 0-11
        const day = String(exp_date.getUTCDate()).padStart(2, '0');

        expiration_date.value = `${year}-${month}-${day}`;
    };

    // Calcular al cargar si hay un valor inicial
    calculateExpirationDate();

    // Escuchar cambios en la fecha de elaboración
    production_date.addEventListener('input', calculateExpirationDate);
});










