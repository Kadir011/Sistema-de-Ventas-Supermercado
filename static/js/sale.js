// Variables globales
const IVA_RATE = 0.15;
let currentRow = 0;

document.addEventListener('DOMContentLoaded', function() {
    // Obtener los datos iniciales
    const initialDetails = JSON.parse(document.getElementById('saleForm').dataset.initialDetails || '[]');
    const initialTotals = JSON.parse(document.getElementById('saleForm').dataset.initialTotals || '{}');

    // Depuración: Verificar los datos iniciales
    console.log('initialDetails:', initialDetails);
    console.log('initialTotals:', initialTotals);

    // Precargar datos iniciales en los campos del formulario
    if (initialDetails.length > 0) {
        console.log('Cargando detalles iniciales...');
        initialDetails.forEach(detail => {
            console.log('Añadiendo detalle:', detail);
            addDetailRowWithData(detail);
        });
        calculateTotals(); // Recalcular totales después de cargar los detalles
    } else {
        console.log('No hay detalles iniciales, añadiendo una fila vacía...');
        addDetailRow();
    }

    // Precargar totales y otros campos
    if (initialTotals.subtotal !== undefined) {
        console.log('Precargando totales...');
        document.querySelector('input[name="subtotal"]').value = initialTotals.subtotal.toFixed(2);
        document.querySelector('input[name="iva"]').value = initialTotals.iva.toFixed(2);
        document.querySelector('input[name="discount"]').value = initialTotals.discount.toFixed(2);
        document.querySelector('input[name="total"]').value = initialTotals.total.toFixed(2);
    } else {
        console.log('No hay totales iniciales, calculando desde cero...');
        calculateTotals();
    }

    document.getElementById('add-product').addEventListener('click', addDetailRow);
    document.getElementById('saleForm').addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) saveSale();
    });
    document.querySelector('input[name="discount"]').addEventListener('input', calculateTotals);
    initProductModal();
});

/**
 * Agrega una nueva fila de detalle de venta
 */
function addDetailRow() {
    const template = document.getElementById('detail-row-template');
    const tbody = document.getElementById('sale-details');
    const clone = document.importNode(template.content, true);
    const row = clone.querySelector('.detail-row');
    row.dataset.rowId = currentRow++;

    const productSelect = row.querySelector('.product-select');
    const quantityInput = row.querySelector('.quantity-input');
    const deleteButton = row.querySelector('.delete-row');

    productSelect.addEventListener('change', () => updateRowPricesAndStock(row.dataset.rowId));
    quantityInput.addEventListener('input', () => updateRowPricesAndStock(row.dataset.rowId));
    deleteButton.addEventListener('click', function() {
        if (document.querySelectorAll('.detail-row').length > 1) {
            const selectedOption = productSelect.options[productSelect.selectedIndex];
            if (selectedOption) {
                const initialStock = parseInt(selectedOption.dataset.stock) || 0;
                const quantity = parseInt(quantityInput.value) || 0;
                alert(`Stock devuelto (simulado): ${initialStock + quantity}`);
            }
            row.remove();
            calculateTotals();
        } else {
            alert('Debe haber al menos un producto en la venta');
        }
    });

    if (tbody.children.length === 0) deleteButton.style.visibility = 'hidden';
    tbody.appendChild(clone);
    showProductModal(row.dataset.rowId);
}

/**
 * Agrega una fila con datos iniciales (para edición)
 */
function addDetailRowWithData(detail) {
    console.log('Ejecutando addDetailRowWithData con detalle:', detail);

    const template = document.getElementById('detail-row-template');
    const tbody = document.getElementById('sale-details');
    const clone = document.importNode(template.content, true);
    const row = clone.querySelector('.detail-row');
    row.dataset.rowId = currentRow++;

    const productSelect = row.querySelector('.product-select');
    const quantityInput = row.querySelector('.quantity-input');
    const priceInput = row.querySelector('.price-input');
    const subtotalInput = row.querySelector('.subtotal-input');
    const deleteButton = row.querySelector('.delete-row');

    let option = document.createElement('option');
    option.value = detail.product;
    option.textContent = `Producto: ${detail.name}`;
    option.dataset.price = detail.price;
    option.dataset.stock = detail.stock;
    productSelect.appendChild(option);
    productSelect.value = detail.product;

    quantityInput.value = detail.quantity;
    quantityInput.dataset.initialQuantity = detail.quantity; // Guardar cantidad inicial para stock
    priceInput.value = detail.price.toFixed(2);
    subtotalInput.value = detail.subtotal.toFixed(2);

    productSelect.addEventListener('change', () => updateRowPricesAndStock(row.dataset.rowId));
    quantityInput.addEventListener('input', () => updateRowPricesAndStock(row.dataset.rowId));
    deleteButton.addEventListener('click', function() {
        if (document.querySelectorAll('.detail-row').length > 1) {
            const initialStock = parseInt(option.dataset.stock) || 0;
            const quantity = parseInt(quantityInput.value) || 0;
            alert(`Stock devuelto (simulado): ${initialStock + quantity}`);
            row.remove();
            calculateTotals();
        } else {
            alert('Debe haber al menos un producto en la venta');
        }
    });

    if (tbody.children.length === 0) deleteButton.style.visibility = 'hidden';
    console.log('Añadiendo fila al tbody:', row);
    tbody.appendChild(clone);
}

/**
 * Actualiza precios, subtotal y simula stock en tiempo real
 */
function updateRowPricesAndStock(rowId) {
    const row = document.querySelector(`.detail-row[data-row-id="${rowId}"]`);
    if (!row) return;

    const productSelect = row.querySelector('.product-select');
    const quantityInput = row.querySelector('.quantity-input');
    const priceInput = row.querySelector('.price-input');
    const subtotalInput = row.querySelector('.subtotal-input');

    const selectedOption = productSelect.options[productSelect.selectedIndex];
    if (selectedOption && selectedOption.value) {
        const price = parseFloat(selectedOption.dataset.price) || 0;
        let quantity = parseInt(quantityInput.value) || 1;
        if (quantity < 1) quantity = 1;
        quantityInput.value = quantity;

        priceInput.value = price.toFixed(2);
        subtotalInput.value = (price * quantity).toFixed(2);

        // Simular stock en tiempo real
        const initialStock = parseInt(selectedOption.dataset.stock) || 0;
        const initialQuantity = parseInt(quantityInput.dataset.initialQuantity) || 0;
        const newStock = initialStock + (initialQuantity - quantity);
        alert(`Stock disponible (simulado): ${newStock}`);
    } else {
        priceInput.value = '0.00';
        subtotalInput.value = '0.00';
    }
    calculateTotals();
}

/**
 * Calcula los totales de la venta
 */
function calculateTotals() {
    const subtotalInputs = document.querySelectorAll('.subtotal-input');
    const subtotalField = document.querySelector('input[name="subtotal"]');
    const ivaField = document.querySelector('input[name="iva"]');
    const discountField = document.querySelector('input[name="discount"]');
    const totalField = document.querySelector('input[name="total"]');

    let subtotal = 0;
    subtotalInputs.forEach(input => subtotal += parseFloat(input.value) || 0);
    const iva = subtotal * IVA_RATE;
    const discount = parseFloat(discountField.value) || 0;
    const total = subtotal + iva - discount;

    subtotalField.value = subtotal.toFixed(2);
    ivaField.value = iva.toFixed(2);
    totalField.value = total.toFixed(2);
}

/**
 * Valida el formulario antes de enviarlo
 */
function validateForm() {
    const productSelects = document.querySelectorAll('.product-select');
    let hasProducts = false;

    for (const select of productSelects) {
        if (select.value) {
            hasProducts = true;
            break;
        }
    }

    if (!hasProducts) {
        alert('Debe seleccionar al menos un producto para la venta');
        return false;
    }

    const customerSelect = document.querySelector('select[name="customer"]');
    if (!customerSelect.value) {
        alert('Debe seleccionar un cliente');
        return false;
    }

    const sellerSelect = document.querySelector('select[name="seller"]');
    if (!sellerSelect.value) {
        alert('Debe seleccionar un vendedor');
        return false;
    }

    const paymentSelect = document.querySelector('select[name="payment"]');
    if (!paymentSelect.value) {
        alert('Debe seleccionar una forma de pago');
        return false;
    }
    return true;
}

/**
 * Guarda la venta y sus detalles
 */
function saveSale() {
    const saleData = {
        customer: document.querySelector('select[name="customer"]').value,
        seller: document.querySelector('select[name="seller"]').value,
        payment: document.querySelector('select[name="payment"]').value,
        sale_date: document.querySelector('input[name="sale_date"]').value,
        subtotal: document.querySelector('input[name="subtotal"]').value,
        iva: document.querySelector('input[name="iva"]').value,
        discount: document.querySelector('input[name="discount"]').value,
        total: document.querySelector('input[name="total"]').value,
        details: []
    };

    const rows = document.querySelectorAll('.detail-row');
    rows.forEach(row => {
        const productSelect = row.querySelector('.product-select');
        const quantityInput = row.querySelector('.quantity-input');
        const priceInput = row.querySelector('.price-input');
        const subtotalInput = row.querySelector('.subtotal-input');

        if (productSelect.value && quantityInput.value && priceInput.value && subtotalInput.value) {
            saleData.details.push({
                product: productSelect.value,
                quantity: quantityInput.value,
                price: priceInput.value,
                subtotal: subtotalInput.value
            });
        }
    });

    console.log('Datos enviados:', JSON.stringify(saleData));

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(window.location.href, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify(saleData)
    })
    .then(response => response.ok ? response.json() : response.text().then(text => { throw new Error(text || 'Error desconocido'); }))
    .then(data => {
        if (data.success) window.location.href = data.redirect_url;
        else alert(data.error || 'Error al guardar la venta');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al guardar la venta: ' + error.message);
    });
}

/**
 * Inicializa el modal de selección de productos
 */
function initProductModal() {
    const modal = document.getElementById('productModal');
    const closeButton = document.getElementById('closeModal');
    const searchInput = document.getElementById('productSearch');

    closeButton.addEventListener('click', () => modal.classList.add('hidden'));
    searchInput.addEventListener('input', () => filterProducts(this.value));
    window.addEventListener('click', event => {
        if (event.target === modal) modal.classList.add('hidden');
    });
}

/**
 * Muestra el modal de productos para seleccionar
 */
function showProductModal(rowId) {
    const modal = document.getElementById('productModal');
    const productList = document.getElementById('productList');

    productList.innerHTML = '';
    fetch('/api/products/')
        .then(response => response.json())
        .then(products => {
            products.forEach(product => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="py-2">${product.name}</td>
                    <td class="py-2">${product.price.toFixed(2)}$</td>
                    <td class="py-2">${product.stock}</td>
                    <td class="py-2">
                        <button type="button" class="select-product bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded"
                            data-id="${product.id}" data-name="${product.name}" data-price="${product.price}" data-stock="${product.stock}">
                            Seleccionar
                        </button>
                    </td>
                `;
                row.querySelector('.select-product').addEventListener('click', () => {
                    selectProduct(rowId, product.id, product.name, product.price, product.stock);
                    modal.classList.add('hidden');
                });
                productList.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error al cargar productos:', error);
            productList.innerHTML = '<tr><td colspan="4" class="py-2 text-center">Error al cargar productos</td></tr>';
        });

    modal.classList.remove('hidden');
}

/**
 * Filtra la lista de productos en el modal
 */
function filterProducts(query) {
    const rows = document.querySelectorAll('#productList tr');
    const lowerQuery = query.toLowerCase();
    rows.forEach(row => {
        const productName = row.querySelector('td:first-child').textContent.toLowerCase();
        row.style.display = productName.includes(lowerQuery) ? '' : 'none';
    });
}

/**
 * Selecciona un producto para una fila específica
 */
function selectProduct(rowId, productId, productName, productPrice, productStock) {
    const row = document.querySelector(`.detail-row[data-row-id="${rowId}"]`);
    if (!row) return;

    const productSelect = row.querySelector('.product-select');
    let option = Array.from(productSelect.options).find(opt => opt.value == productId);
    if (!option) {
        option = document.createElement('option');
        option.value = productId;
        option.textContent = `Producto: ${productName}`;
        option.dataset.price = productPrice;
        option.dataset.stock = productStock;
        productSelect.appendChild(option);
    }
    option.selected = true;
    updateRowPricesAndStock(rowId);
}




