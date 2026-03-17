// Variables globales
const IVA_RATE = 0.15;
let currentRow = 0;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando carga del formulario de ventas...');
    
    const saleForm = document.getElementById('saleForm');
    let initialDetails = [];
    let initialTotals = {};
    
    try {
        const detailsAttr = saleForm.dataset.initialDetails;
        const totalsAttr = saleForm.dataset.initialTotals;
        
        if (detailsAttr && detailsAttr !== '[]') {
            initialDetails = JSON.parse(detailsAttr);
        }
        if (totalsAttr && totalsAttr !== '{}') {
            initialTotals = JSON.parse(totalsAttr);
        }
    } catch (error) {
        console.error('Error al parsear datos iniciales:', error);
    }

    if (initialDetails && initialDetails.length > 0) {
        initialDetails.forEach(detail => {
            addDetailRowWithData(detail);
        });
        setTimeout(() => { calculateTotals(); }, 100);
    } else {
        addDetailRow();
    }

    if (initialTotals && Object.keys(initialTotals).length > 0) {
        document.querySelector('input[name="subtotal"]').value = parseFloat(initialTotals.subtotal || 0).toFixed(2);
        document.querySelector('input[name="iva"]').value = parseFloat(initialTotals.iva || 0).toFixed(2);
        document.querySelector('input[name="discount"]').value = parseFloat(initialTotals.discount || 0).toFixed(2);
        document.querySelector('input[name="total"]').value = parseFloat(initialTotals.total || 0).toFixed(2);
    }

    document.getElementById('add-product').addEventListener('click', addDetailRow);
    document.getElementById('saleForm').addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) saveSale();
    });
    document.querySelector('input[name="discount"]').addEventListener('input', calculateTotals);
    initProductModal();
});

function addDetailRow() {
    const template = document.getElementById('detail-row-template');
    const tbody = document.getElementById('sale-details').querySelector('tbody');
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
            row.remove();
            calculateTotals();
        } else {
            alert('Debe haber al menos un producto en la venta');
        }
    });

    tbody.appendChild(clone);
    showProductModal(row.dataset.rowId);
}

function addDetailRowWithData(detail) {
    const template = document.getElementById('detail-row-template');
    const tbody = document.getElementById('sale-details').querySelector('tbody');
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
    option.textContent = detail.name;
    option.dataset.price = detail.price;
    option.dataset.stock = detail.stock + detail.quantity;
    option.selected = true;
    productSelect.appendChild(option);

    quantityInput.value = detail.quantity;
    quantityInput.dataset.initialQuantity = detail.quantity;
    priceInput.value = parseFloat(detail.price).toFixed(2);
    subtotalInput.value = parseFloat(detail.subtotal).toFixed(2);

    productSelect.addEventListener('change', () => updateRowPricesAndStock(row.dataset.rowId));
    quantityInput.addEventListener('input', () => updateRowPricesAndStock(row.dataset.rowId));
    deleteButton.addEventListener('click', function() {
        if (document.querySelectorAll('.detail-row').length > 1) {
            row.remove();
            calculateTotals();
        } else {
            alert('Debe haber al menos un producto en la venta');
        }
    });

    tbody.appendChild(clone);
}

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
        const stock = parseInt(selectedOption.dataset.stock) || 0;
        let quantity = parseInt(quantityInput.value) || 1;
        
        if (quantity < 1) quantity = 1;
        if (quantity > stock) {
            alert(`Stock disponible: ${stock} unidades`);
            quantity = stock;
        }
        
        quantityInput.value = quantity;
        priceInput.value = price.toFixed(2);
        subtotalInput.value = (price * quantity).toFixed(2);
    } else {
        priceInput.value = '0.00';
        subtotalInput.value = '0.00';
    }
    calculateTotals();
}

function calculateTotals() {
    const subtotalInputs = document.querySelectorAll('.subtotal-input');
    const subtotalField = document.querySelector('input[name="subtotal"]');
    const ivaField = document.querySelector('input[name="iva"]');
    const discountField = document.querySelector('input[name="discount"]');
    const totalField = document.querySelector('input[name="total"]');

    let subtotal = 0;
    subtotalInputs.forEach(input => {
        subtotal += parseFloat(input.value) || 0;
    });
    
    const iva = subtotal * IVA_RATE;
    const discount = parseFloat(discountField.value) || 0;
    const total = subtotal + iva - discount;

    subtotalField.value = subtotal.toFixed(2);
    ivaField.value = iva.toFixed(2);
    totalField.value = total.toFixed(2);
}

function validateForm() {
    const customerSelect = document.querySelector('select[name="customer"]');
    if (!customerSelect.value) {
        alert('Debe seleccionar un cliente');
        customerSelect.focus();
        return false;
    }

    const sellerSelect = document.querySelector('select[name="seller"]');
    if (!sellerSelect.value) {
        alert('Debe seleccionar un vendedor');
        sellerSelect.focus();
        return false;
    }

    const paymentSelect = document.querySelector('select[name="payment"]');
    if (!paymentSelect.value) {
        alert('Debe seleccionar una forma de pago');
        paymentSelect.focus();
        return false;
    }

    const productSelects = document.querySelectorAll('.product-select');
    let hasProducts = false;
    for (const select of productSelects) {
        if (select.value) { hasProducts = true; break; }
    }

    if (!hasProducts) {
        alert('Debe seleccionar al menos un producto para la venta');
        return false;
    }

    return true;
}

function saveSale() {
    // ── Idempotencia: leer la clave generada en el GET ────────────────────
    // El campo hidden #idempotency_key_field fue renderizado por el servidor
    // con un UUID único al abrir este formulario. Se envía con cada POST.
    // Si el mismo request llega dos veces, el backend devuelve la venta
    // existente sin crear duplicados.
    const idempotencyKey = document.getElementById('idempotency_key_field')?.value || '';

    // ── Protección en el cliente: deshabilitar el botón de guardar ────────
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        if (submitBtn.dataset.submitted) return;   // segundo clic bloqueado
        submitBtn.dataset.submitted = 'true';
        submitBtn.disabled = true;
        submitBtn.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Guardando...";
    }

    const saleData = {
        customer: document.querySelector('select[name="customer"]').value,
        seller: document.querySelector('select[name="seller"]').value,
        payment: document.querySelector('select[name="payment"]').value,
        sale_date: document.querySelector('input[name="sale_date"]').value,
        subtotal: document.querySelector('input[name="subtotal"]').value,
        iva: document.querySelector('input[name="iva"]').value,
        discount: document.querySelector('input[name="discount"]').value,
        total: document.querySelector('input[name="total"]').value,
        idempotency_key: idempotencyKey,   // ← incluido en el payload
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

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(saleData)
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text || 'Error desconocido'); });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            // Re-habilitar el botón si el servidor rechaza la petición
            if (submitBtn) {
                submitBtn.disabled = false;
                delete submitBtn.dataset.submitted;
                submitBtn.innerHTML = "<i class='bx bx-save'></i> Guardar";
            }
            alert(data.error || 'Error al guardar la venta');
        }
    })
    .catch(error => {
        if (submitBtn) {
            submitBtn.disabled = false;
            delete submitBtn.dataset.submitted;
            submitBtn.innerHTML = "<i class='bx bx-save'></i> Guardar";
        }
        console.error('Error:', error);
        alert('Error al guardar la venta: ' + error.message);
    });
}

function initProductModal() {
    const modal = document.getElementById('productModal');
    const closeButton = document.getElementById('closeModal');
    const searchInput = document.getElementById('productSearch');

    closeButton.addEventListener('click', () => modal.classList.add('hidden'));
    searchInput.addEventListener('input', function() { filterProducts(this.value); });
    window.addEventListener('click', event => {
        if (event.target === modal) modal.classList.add('hidden');
    });
}

function showProductModal(rowId) {
    const modal = document.getElementById('productModal');
    const productList = document.getElementById('productList');

    productList.innerHTML = '<tr><td colspan="4" class="py-2 text-center">Cargando productos...</td></tr>';
    
    fetch('/api/products/')
        .then(response => response.json())
        .then(products => {
            productList.innerHTML = '';
            if (products.length === 0) {
                productList.innerHTML = '<tr><td colspan="4" class="py-2 text-center">No hay productos disponibles</td></tr>';
                return;
            }
            products.forEach(product => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="py-2 px-4 border-b">${product.name}</td>
                    <td class="py-2 px-4 border-b">$${parseFloat(product.price).toFixed(2)}</td>
                    <td class="py-2 px-4 border-b">${product.stock}</td>
                    <td class="py-2 px-4 border-b text-center">
                        <button type="button" class="select-product bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded"
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
            productList.innerHTML = '<tr><td colspan="4" class="py-2 text-center text-red-500">Error al cargar productos</td></tr>';
        });

    modal.classList.remove('hidden');
}

function filterProducts(query) {
    const rows = document.querySelectorAll('#productList tr');
    const lowerQuery = query.toLowerCase();
    rows.forEach(row => {
        const productName = row.querySelector('td:first-child')?.textContent.toLowerCase();
        if (productName) {
            row.style.display = productName.includes(lowerQuery) ? '' : 'none';
        }
    });
}

function selectProduct(rowId, productId, productName, productPrice, productStock) {
    const row = document.querySelector(`.detail-row[data-row-id="${rowId}"]`);
    if (!row) return;

    const productSelect = row.querySelector('.product-select');
    while (productSelect.options.length > 1) { productSelect.remove(1); }
    
    let option = document.createElement('option');
    option.value = productId;
    option.textContent = productName;
    option.dataset.price = productPrice;
    option.dataset.stock = productStock;
    option.selected = true;
    productSelect.appendChild(option);
    
    updateRowPricesAndStock(rowId);
}