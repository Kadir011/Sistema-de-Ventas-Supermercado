document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('scannerModal');
    const resultModal = document.getElementById('resultModal');
    const openModalButton = document.getElementById('openModal');
    const closeModalButton = document.getElementById('closeModal');
    const closeResultModalButton = document.getElementById('closeResultModal');
    const cameraView = document.getElementById('cameraView');
    const resultContent = document.getElementById('resultContent');
    const barcodeOverlay = document.getElementById('barcodeOverlay');
    const canvas = document.createElement('canvas');
    const beepSound = new Audio('/static/sounds/barcode_sound.mp3'); // Cargar el sonido
    let videoStream = null;
    let scanning = false;

    openModalButton.addEventListener('click', function () {
        modal.classList.remove('hidden');
        startCamera();
    });

    closeModalButton.addEventListener('click', function () {
        modal.classList.add('hidden');
        stopCamera();
    });

    closeResultModalButton.addEventListener('click', function () {
        resultModal.classList.add('hidden');
        modal.classList.remove('hidden');
        startCamera();
    });

    function startCamera() {
        navigator.mediaDevices
            .getUserMedia({ video: { facingMode: 'environment' } })
            .then(function (stream) {
                videoStream = stream;
                cameraView.srcObject = stream;
                scanning = true;
                barcodeOverlay.classList.remove('border-green-500');
                barcodeOverlay.classList.add('border-red-500'); // Marco rojo al iniciar
                requestAnimationFrame(scanBarcode);
            })
            .catch(function (err) {
                console.error('Error al acceder a la cámara:', err);
                alert('No se pudo acceder a la cámara.');
            });
    }

    function stopCamera() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
            scanning = false;
        }
    }

    function scanBarcode() {
        if (!scanning) return;

        if (cameraView.videoWidth === 0 || cameraView.videoHeight === 0) {
            requestAnimationFrame(scanBarcode);
            return;
        }

        const context = canvas.getContext('2d');
        canvas.width = cameraView.videoWidth;
        canvas.height = cameraView.videoHeight;
        context.drawImage(cameraView, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(function (blob) {
            let formData = new FormData();
            formData.append('barcode', blob);

            fetch('/scan_barcode/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Cambiar el marco a verde y reproducir el pitido
                        barcodeOverlay.classList.remove('border-red-500');
                        barcodeOverlay.classList.add('border-green-500');
                        beepSound.play().catch(error => console.log('Error al reproducir sonido:', error));

                        // Mostrar resultado después de un pequeño retraso para que se vea el cambio
                        setTimeout(() => {
                            resultContent.innerHTML = `
                                <img src="${data.image_url}" alt="Imagen del producto" class="w-full max-w-xs mx-auto mb-4 rounded-lg shadow-md">
                                <p class="text-lg font-semibold text-gray-800 mb-2"><strong>Nombre:</strong> ${data.product_name}</p>
                                <p class="text-lg font-semibold text-gray-800 mb-2"><strong>Precio:</strong> $${data.price}</p>
                                <p class="text-lg font-semibold text-gray-800 mb-4"><strong>Stock:</strong> ${data.stock}</p>
                            `;
                            resultModal.classList.remove('hidden');
                            modal.classList.add('hidden');
                            stopCamera();
                        }, 500); // Retraso de 500ms para que el usuario note el cambio a verde
                    } else {
                        // Mantener el marco rojo y seguir escaneando
                        barcodeOverlay.classList.remove('border-green-500');
                        barcodeOverlay.classList.add('border-red-500');
                        requestAnimationFrame(scanBarcode);
                    }
                })
                .catch(error => {
                    console.error('Error en la solicitud:', error);
                    barcodeOverlay.classList.remove('border-green-500');
                    barcodeOverlay.classList.add('border-red-500');
                    requestAnimationFrame(scanBarcode);
                });
        }, 'image/png');
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});









