const modal = document.getElementById('detailModal');
const modalBody = document.getElementById('modalBody');
const modalContainer = document.getElementById('modalContentContainer');

function openDetailModal(url) {
    // Mostrar modal y spinner
    modal.classList.remove('hidden');
    // Pequeña animación de entrada
    setTimeout(() => {
        modalContainer.classList.remove('scale-95');
        modalContainer.classList.add('scale-100');
    }, 10);

    // Fetch del contenido
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Error al cargar');
            return response.text();
        })
        .then(html => {
            modalBody.innerHTML = html;
        })
        .catch(error => {
            modalBody.innerHTML = `
                    <div class="text-center text-red-500 py-8">
                        <i class='bx bx-error-circle text-4xl mb-2'></i>
                        <p>Error al cargar los detalles de la venta.</p>
                    </div>
                `;
        });
}

function closeDetailModal() {
    modalContainer.classList.remove('scale-100');
    modalContainer.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
        modalBody.innerHTML = `
                <div class="flex justify-center items-center py-10">
                    <i class='bx bx-loader-alt bx-spin text-4xl text-blue-600'></i>
                </div>
            `;
    }, 300); // Esperar a que termine la animación
}

// Cerrar al hacer click fuera del modal
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        closeDetailModal();
    }
});