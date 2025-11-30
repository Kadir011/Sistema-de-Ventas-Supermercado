document.addEventListener('DOMContentLoaded', () => {
    const barcodeInput = document.getElementById('id_barcode');
    // Nota: La validación visual de longitud (Amarillo/Verde/Rojo) 
    // ahora es manejada globalmente por validations.js.
    // Este script se encarga exclusivamente de verificar la validez MATEMÁTICA del EAN-13
    // una vez que el campo está completo.

    if (!barcodeInput) return;

    const form = barcodeInput.closest('form');
    let errorElement = null;

    // Función para validar código de barras EAN-13 (Algoritmo matemático)
    function validateBarcodeMath(barcode) {
        if (barcode.length !== 13 || isNaN(barcode)) {
            return false;
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
            errorElement.className = 'text-red-500 text-sm mt-2 barcode-error';
            barcodeInput.parentNode.appendChild(errorElement);
        } 
        errorElement.textContent = message;
        // Forzamos borde rojo si la matemática falla, aunque la longitud sea correcta
        barcodeInput.classList.remove('border-green-500', 'border-yellow-500');
        barcodeInput.classList.add('border-red-500');
    } 

    function clearError() {
        if (errorElement) {
            errorElement.remove();
            errorElement = null;
        }
        // Si borramos el error matemático y la longitud es 13, validations.js pondrá el borde verde automáticamente
        // al disparar el evento input, o podemos dejarlo como está.
    } 

    // Validar solo cuando esté completo o al cambiar
    barcodeInput.addEventListener('input', () => {
        const barcode = barcodeInput.value.trim();
        // Solo validamos matemáticamente si ya completó los 13 dígitos
        if (barcode.length === 13) {
            if (validateBarcodeMath(barcode)) {
                clearError();
                // Validations.js se encargará de ponerlo verde por longitud
            } else {
                showError('El dígito de control del código de barras es inválido.');
            }
        } else {
            clearError(); // Limpiamos error matemático mientras escribe (validations.js pondrá amarillo)
        }
    }); 

    // Bloqueo adicional al enviar
    form.addEventListener('submit', (event) => {
        const barcode = barcodeInput.value.trim();
        // Si tiene longitud correcta pero matemática incorrecta
        if (barcode.length === 13 && !validateBarcodeMath(barcode)) {
            event.preventDefault();
            showError('Código de barras inválido (Error en dígito verificador).');
        }
    });
});