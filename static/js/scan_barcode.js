document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('scannerModal');
    const resultModal = document.getElementById('resultModal');
    const openModalButton = document.getElementById('openModal');
    const closeModalButton = document.getElementById('closeModal');
    const closeResultModalButton = document.getElementById('closeResultModal');
    const cameraView = document.getElementById('cameraView');
    const resultContent = document.getElementById('resultContent');
    const barcodeOverlay = document.getElementById('barcodeOverlay');
    const scanningStatus = document.getElementById('scanningStatus');
    const canvas = document.createElement('canvas');
    const beepSound = new Audio('/static/sounds/barcode_sound.mp3');
    
    let videoStream = null;
    let scanning = false;
    let scanningInterval = null;
    let lastScanTime = 0;
    const SCAN_COOLDOWN = 2000; // 2 segundos entre escaneos

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

    function updateStatus(message, type = 'info') {
        scanningStatus.textContent = message;
        scanningStatus.className = 'text-center mt-2 font-semibold ';
        
        if (type === 'success') {
            scanningStatus.classList.add('text-green-600');
        } else if (type === 'error') {
            scanningStatus.classList.add('text-red-600');
        } else if (type === 'scanning') {
            scanningStatus.classList.add('text-blue-600');
        } else {
            scanningStatus.classList.add('text-gray-600');
        }
    }

    function startCamera() {
        // Solicitar la mejor calidad de cámara posible
        const constraints = {
            video: {
                facingMode: { ideal: 'environment' },
                width: { ideal: 1920 },
                height: { ideal: 1080 },
                focusMode: { ideal: 'continuous' },
                zoom: { ideal: 1.0 }
            }
        };

        navigator.mediaDevices
            .getUserMedia(constraints)
            .then(function (stream) {
                videoStream = stream;
                cameraView.srcObject = stream;
                
                // Esperar a que el video esté listo
                cameraView.onloadedmetadata = function() {
                    scanning = true;
                    barcodeOverlay.classList.remove('border-green-500');
                    barcodeOverlay.classList.add('border-red-500');
                    updateStatus('Enfoque el código de barras dentro del marco', 'scanning');
                    
                    // Iniciar escaneo continuo
                    scanningInterval = setInterval(scanBarcode, 300); // Escanear cada 300ms
                };
            })
            .catch(function (err) {
                console.error('Error al acceder a la cámara:', err);
                updateStatus('No se pudo acceder a la cámara', 'error');
                alert('No se pudo acceder a la cámara. Verifique los permisos.');
            });
    }

    function stopCamera() {
        if (scanningInterval) {
            clearInterval(scanningInterval);
            scanningInterval = null;
        }
        
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
            scanning = false;
        }
        
        updateStatus('', 'info');
    }

    function captureFrame() {
        if (cameraView.videoWidth === 0 || cameraView.videoHeight === 0) {
            return null;
        }

        const context = canvas.getContext('2d');
        canvas.width = cameraView.videoWidth;
        canvas.height = cameraView.videoHeight;
        
        // Capturar el frame completo
        context.drawImage(cameraView, 0, 0, canvas.width, canvas.height);
        
        return canvas;
    }

    function scanBarcode() {
        if (!scanning) return;

        const now = Date.now();
        if (now - lastScanTime < SCAN_COOLDOWN) {
            return;
        }

        const frame = captureFrame();
        if (!frame) {
            return;
        }

        frame.toBlob(function (blob) {
            if (!blob) return;

            let formData = new FormData();
            formData.append('barcode', blob, 'barcode.png');

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
                    lastScanTime = Date.now();
                    
                    // Cambiar el marco a verde y reproducir sonido
                    barcodeOverlay.classList.remove('border-red-500');
                    barcodeOverlay.classList.add('border-green-500');
                    updateStatus('¡Código detectado!', 'success');
                    
                    // Reproducir sonido
                    beepSound.play().catch(error => {
                        console.log('No se pudo reproducir el sonido:', error);
                    });

                    // Detener el escaneo
                    stopCamera();

                    // Mostrar resultado después de un breve retraso
                    setTimeout(() => {
                        displayResult(data);
                        resultModal.classList.remove('hidden');
                        modal.classList.add('hidden');
                    }, 500);
                } else {
                    // Continuar escaneando sin mostrar errores constantes
                    barcodeOverlay.classList.remove('border-green-500');
                    barcodeOverlay.classList.add('border-yellow-500');
                }
            })
            .catch(error => {
                console.error('Error en la solicitud:', error);
                // No detener el escaneo por errores de red
            });
        }, 'image/png', 0.95);
    }

    function displayResult(data) {
        resultContent.innerHTML = `
            <div class="space-y-4">
                <img src="${data.image_url}" 
                     alt="${data.product_name}" 
                     class="w-full max-w-xs mx-auto rounded-lg shadow-md object-cover"
                     style="max-height: 250px;">
                
                <div class="bg-gray-50 p-4 rounded-lg space-y-2">
                    <div class="flex justify-between items-center border-b pb-2">
                        <span class="font-semibold text-gray-700">Código:</span>
                        <span class="text-gray-900 font-mono">${data.barcode}</span>
                    </div>
                    
                    <div class="flex justify-between items-center border-b pb-2">
                        <span class="font-semibold text-gray-700">Producto:</span>
                        <span class="text-gray-900 font-semibold">${data.product_name}</span>
                    </div>
                    
                    <div class="flex justify-between items-center border-b pb-2">
                        <span class="font-semibold text-gray-700">Precio:</span>
                        <span class="text-green-600 font-bold text-xl">$${data.price.toFixed(2)}</span>
                    </div>
                    
                    <div class="flex justify-between items-center border-b pb-2">
                        <span class="font-semibold text-gray-700">Stock:</span>
                        <span class="text-blue-600 font-semibold">${data.stock} unidades</span>
                    </div>
                    
                    ${data.category ? `
                    <div class="flex justify-between items-center border-b pb-2">
                        <span class="font-semibold text-gray-700">Categoría:</span>
                        <span class="text-gray-900">${data.category}</span>
                    </div>
                    ` : ''}
                    
                    ${data.brand ? `
                    <div class="flex justify-between items-center">
                        <span class="font-semibold text-gray-700">Marca:</span>
                        <span class="text-gray-900">${data.brand}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
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