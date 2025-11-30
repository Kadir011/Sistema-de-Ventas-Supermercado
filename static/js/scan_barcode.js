document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('scannerModal');
    const resultModal = document.getElementById('resultModal');
    const openModalButton = document.getElementById('openModal');
    const closeModalButton = document.getElementById('closeModal');
    const closeResultModalButton = document.getElementById('closeResultModal');
    const scanningStatus = document.getElementById('scanningStatus');
    const resultContent = document.getElementById('resultContent');
    const beepSound = new Audio('/static/sounds/barcode_sound.mp3');

    let isScanning = false;
    let lastScannedCode = null;
    let lastScanTime = 0;

    // Exponer inicio globalmente por si se necesita reiniciar desde otro script
    window.initQuagga = startScanner;

    openModalButton.addEventListener('click', function () {
        modal.classList.remove('hidden');
        startScanner();
    });

    closeModalButton.addEventListener('click', function () {
        stopScanner();
        modal.classList.add('hidden');
    });

    closeResultModalButton.addEventListener('click', function () {
        resultModal.classList.add('hidden');
        // Descomenta si quieres que se abra el escáner automáticamente al cerrar el resultado
        // modal.classList.remove('hidden');
        // startScanner();
    });

    function startScanner() {
        if (isScanning) return;

        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: document.querySelector('#interactive'),
                constraints: {
                    facingMode: "environment", // Usar cámara trasera
                    width: { min: 640, ideal: 1280, max: 1920 }, // Resolución HD para mejor precisión
                    height: { min: 480, ideal: 720, max: 1080 },
                    aspectRatio: { min: 1, max: 2 },
                    // Intentar forzar enfoque continuo (vital para códigos curvos/brillosos)
                    advanced: [{ focusMode: "continuous" }] 
                },
                // IMPORTANTE: Definir área de escaneo. 
                // Solo procesa el rectángulo central (donde está el láser).
                // Ignora el ruido de los bordes, mejorando velocidad y precisión.
                area: { 
                    top: "25%",    // Ignora el 25% superior
                    right: "10%",  // Ignora el 10% derecho
                    left: "10%",   // Ignora el 10% izquierdo
                    bottom: "25%"  // Ignora el 25% inferior
                },
            },
            locator: {
                patchSize: "medium", // 'medium' es buen balance. Usa 'small' si tus códigos son muy pequeños.
                halfSample: true     // true = más rápido, false = más preciso pero lento.
            },
            numOfWorkers: navigator.hardwareConcurrency || 2, // Usa todos los núcleos del CPU disponibles
            decoder: {
                readers: [
                    "ean_reader" // Solo EAN-13 (estándar supermercado) para evitar falsos positivos de otros formatos
                ],
                debug: {
                    drawBoundingBox: false,
                    showFrequency: false,
                    drawScanline: false,
                    showPattern: false
                },
                multiple: false
            },
            locate: true // Ayuda a encontrar el código en la imagen
        }, function (err) {
            if (err) {
                console.error("Error iniciando Quagga:", err);
                scanningStatus.textContent = 'Error: No se pudo acceder a la cámara.';
                scanningStatus.classList.add('bg-red-600');
                return;
            }
            console.log("Cámara iniciada correctamente");
            Quagga.start();
            isScanning = true;
            scanningStatus.textContent = 'Enfoque el código en el centro...';
            scanningStatus.classList.remove('bg-red-600', 'bg-green-600');
            scanningStatus.classList.add('bg-black');
        });

        // Feedback Visual: Dibuja cajas verdes cuando detecta "algo" parecido a un código
        Quagga.onProcessed(function (result) {
            var drawingCtx = Quagga.canvas.ctx.overlay,
                drawingCanvas = Quagga.canvas.dom.overlay;

            if (result) {
                if (result.boxes) {
                    drawingCtx.clearRect(0, 0, parseInt(drawingCanvas.getAttribute("width")), parseInt(drawingCanvas.getAttribute("height")));
                    result.boxes.filter(function (box) {
                        return box !== result.box;
                    }).forEach(function (box) {
                        Quagga.ImageDebug.drawPath(box, { x: 0, y: 1 }, drawingCtx, { color: "green", lineWidth: 2 });
                    });
                }

                if (result.box) {
                    Quagga.ImageDebug.drawPath(result.box, { x: 0, y: 1 }, drawingCtx, { color: "#00F", lineWidth: 2 });
                }

                if (result.codeResult && result.codeResult.code) {
                    Quagga.ImageDebug.drawPath(result.line, { x: 'x', y: 'y' }, drawingCtx, { color: 'red', lineWidth: 3 });
                }
            }
        });

        // Detección Exitosa
        Quagga.onDetected(function (result) {
            const code = result.codeResult.code;
            const now = Date.now();

            // Evitar lecturas múltiples instantáneas (Cooldown de 1.5s)
            if (code === lastScannedCode && (now - lastScanTime < 1500)) {
                return;
            }

            // Validación Matemática EAN-13 (Checksum)
            // Esto evita leer "basura" en empaques con mucho texto o texturas
            if (!validateEAN13(code)) {
                // console.log("Código inválido detectado (checksum fallido):", code);
                return;
            }

            // Si pasa la validación:
            lastScannedCode = code;
            lastScanTime = now;

            // Feedback auditivo y visual inmediato
            beepSound.play().catch(e => console.warn("No se pudo reproducir sonido", e));
            scanningStatus.textContent = `¡Código detectado! Procesando...`;
            scanningStatus.classList.remove('bg-black');
            scanningStatus.classList.add('bg-blue-600');

            // Pausar escáner para ahorrar recursos mientras consultamos al servidor
            stopScanner();

            // Consultar producto
            fetchProduct(code);
        });
    }

    function stopScanner() {
        if (isScanning) {
            Quagga.stop();
            isScanning = false;
            // Limpiar el canvas de dibujo (líneas verdes)
            const canvas = document.querySelector('#interactive canvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }
    }

    // Algoritmo oficial para validar que un EAN-13 es real matemáticamente
    function validateEAN13(barcode) {
        if (barcode.length !== 13 || isNaN(barcode)) return false;
        
        let sum = 0;
        // Sumar pares e impares con peso x1 y x3
        for (let i = 0; i < 12; i++) {
            const digit = parseInt(barcode[i]);
            sum += i % 2 === 0 ? digit : digit * 3;
        }
        
        // Calcular dígito verificador
        const check = (10 - (sum % 10)) % 10;
        
        // Comparar con el último dígito del código escaneado
        return check === parseInt(barcode[12]);
    }

    function fetchProduct(barcode) {
        const formData = new FormData();
        formData.append('barcode', barcode);

        fetch('/scan_barcode/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            modal.classList.add('hidden');
            resultModal.classList.remove('hidden');
            displayResult(data);
            
            // Resetear estado visual
            scanningStatus.classList.remove('bg-blue-600');
            scanningStatus.classList.add('bg-black');
            scanningStatus.textContent = 'Enfoque el código en el centro...';
        })
        .catch(error => {
            console.error('Error de red:', error);
            scanningStatus.textContent = 'Error de conexión. Intente de nuevo.';
            scanningStatus.classList.add('bg-red-600');
            // Si falla la red, reiniciamos el escáner después de un momento
            setTimeout(() => {
                startScanner();
            }, 2000);
        });
    }

    function displayResult(data) {
        if (data.success) {
            resultContent.innerHTML = `
                <div class="space-y-4 animate-fade-in">
                    <img src="${data.image_url}" 
                         alt="${data.product_name}" 
                         class="w-48 h-48 mx-auto rounded-lg shadow-md object-contain bg-white p-2 border border-gray-200">
                    
                    <div class="bg-gray-50 p-4 rounded-xl space-y-3 text-left shadow-inner">
                        <div class="flex justify-between items-center border-b border-gray-200 pb-2">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Código EAN</span>
                            <span class="font-mono font-bold text-gray-800 text-lg tracking-widest">${data.barcode}</span>
                        </div>
                        
                        <div>
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Producto</span>
                            <span class="font-bold text-gray-900 text-xl leading-tight block">${data.product_name}</span>
                        </div>
                        
                        <div class="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm border border-gray-100">
                            <span class="text-gray-600 font-medium">Precio Unitario</span>
                            <span class="text-green-600 font-extrabold text-3xl">$${data.price.toFixed(2)}</span>
                        </div>
                        
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 text-sm">Disponibilidad</span>
                            <div class="flex items-center">
                                <span class="w-3 h-3 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                                <span class="text-gray-800 font-bold">${data.stock} Unidades</span>
                            </div>
                        </div>
                        
                        ${data.category ? `
                        <div class="mt-2 pt-2 border-t border-gray-200 flex justify-between text-xs text-gray-500">
                            <span>${data.category}</span>
                            <span>${data.brand}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
        } else {
            resultContent.innerHTML = `
                <div class="text-center py-8 animate-fade-in">
                    <div class="bg-red-100 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-4 animate-bounce">
                        <i class='bx bx-error text-5xl text-red-500'></i>
                    </div>
                    <h4 class="text-2xl font-bold text-gray-800 mb-2">¡Ups!</h4>
                    <p class="text-gray-600 mb-6 px-4">${data.error || 'El producto escaneado no está registrado o no tiene stock.'}</p>
                    <div class="inline-block bg-gray-100 px-4 py-2 rounded-lg border border-gray-300">
                        <span class="text-xs text-gray-500 block">Código leído:</span>
                        <span class="font-mono font-bold text-gray-700 tracking-wider">${data.barcode}</span>
                    </div>
                </div>
            `;
        }
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