document.addEventListener('DOMContentLoaded', () => {
    const barcodeInput = document.getElementById('id_barcode');
    const form = barcodeInput.closest('form');

    // Mensaje de error dinámico
    let errorElement = null;

    // Función para validar código de barras EAN-13
    function validateBarcode(barcode) {
        if (barcode.length !== 13 || isNaN(barcode)) {
            return false; // Debe ser un número de 13 dígitos
        } 

        let sum = 0;

        // Recorrer los 12 primeros dígitos
        for (let i = 0; i < 12; i++) {
            const digit = parseInt(barcode[i], 10);
            sum += i % 2 === 0 ? digit : digit * 3; // Peso alternado: 1 y 3 
        } 

        // Calcular el dígito de control
        const checkDigit = (10 - (sum % 10)) % 10;

        // Comparar con el último dígito del código
        return checkDigit === parseInt(barcode[12], 10);
    } 

    function showError(message) {
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'text-red-500 text-sm mt-2';
            barcodeInput.parentNode.appendChild(errorElement);
        } 
        errorElement.textContent = message;
        barcodeInput.classList.add('border-red-500');
    } 

    // Ocultar mensaje de error
    function clearError() {
        if (errorElement) {
            errorElement.remove();
            errorElement = null;
        }
        barcodeInput.classList.remove('border-red-500');
    } 

    // Validar en tiempo real
    barcodeInput.addEventListener('input', () => {
        const barcode = barcodeInput.value.trim();
        if (validateBarcode(barcode)) {
            clearError();
            barcodeInput.classList.add('border-green-500');
        } else {
            showError('El código de barras no es válido.');
            barcodeInput.classList.remove('border-green-500');
        }
    }); 

    // Validar al enviar el formulario
    form.addEventListener('submit', (event) => {
        const barcode = barcodeInput.value.trim();
        if (!validateBarcode(barcode)) {
            event.preventDefault(); // Prevenir envío
            showError('El código de barras no es válido. Por favor, corrige el error.');
        }
    });
}); 

