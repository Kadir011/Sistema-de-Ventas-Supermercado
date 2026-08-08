/**
 * scan_barcode.js — Escáner EAN-13 optimizado
 *
 * Correcciones cross-browser aplicadas:
 * - [CRÍTICO] navigator.hardwareConcurrency con fallback robusto (Safari iOS)
 * - [CRÍTICO] advanced camera constraints movidas a applyConstraints() con try/catch
 * - [CRÍTICO] Fallback a cámara frontal si OverconstrainedError en iOS
 * - [INFO] Fallback para facingMode "environment" en dispositivos sin cámara trasera
 */

document.addEventListener('DOMContentLoaded', function () {

    /* ── Elementos del DOM ─────────────────────────────────── */
    const modal             = document.getElementById('scannerModal');
    const resultModal       = document.getElementById('resultModal');
    const openModalButton   = document.getElementById('openModal');
    const closeModalButton  = document.getElementById('closeModal');
    const closeResultModal  = document.getElementById('closeResultModal');
    const scanningStatus    = document.getElementById('scanningStatus');
    const resultContent     = document.getElementById('resultContent');
    const beepSound         = new Audio('/static/sounds/barcode_sound.mp3');
    const voteBar           = document.getElementById('voteProgressBar');
    const voteLabel         = document.getElementById('voteLabel');

    /* ── Estado interno ────────────────────────────────────── */
    let isScanning   = false;
    let voteMap      = {};
    let lastScanTime = 0;
    let stallTimer   = null;
    let stallStage   = 0;

    const VOTES_REQUIRED = 3;

    /* ── Avisos progresivos si el escáner no logra leer nada ──
       Se reinicia cada vez que Quagga detecta CUALQUIER patrón de barras
       (aunque no sea un EAN-13 válido todavía) — eso ya indica que la
       cámara SÍ está viendo algo, solo falta que lo lea bien. Si pasa el
       tiempo sin ni siquiera eso, el problema es de encuadre/luz/enfoque,
       y se lo decimos al usuario en vez de dejarlo esperando a ciegas. */
    const STALL_TIPS = [
        { ms: 8000,  text: '💡 Acerca más el código, a unos 10-15 cm', color: 'blue' },
        { ms: 15000, text: '💡 Mejora la iluminación o evita reflejos en el empaque', color: 'blue' },
        { ms: 25000, text: '💡 Mantén el código bien plano y quieto frente a la cámara', color: 'blue' },
    ];

    function resetStallTimer() {
        clearTimeout(stallTimer);
        stallStage = 0;
        scheduleNextStallTip();
    }

    function scheduleNextStallTip() {
        if (stallStage >= STALL_TIPS.length) return;
        const tip = STALL_TIPS[stallStage];
        stallTimer = setTimeout(() => {
            if (!isScanning) return;
            setStatus(tip.text, tip.color);
            stallStage++;
            scheduleNextStallTip();
        }, stallStage === 0 ? tip.ms : tip.ms - STALL_TIPS[stallStage - 1].ms);
    }

    function clearStallTimer() {
        clearTimeout(stallTimer);
        stallStage = 0;
    }

    /* ── Calcular workers de forma robusta (CRÍTICO — Safari iOS) ──
       navigator.hardwareConcurrency puede ser undefined en Safari iOS
       antiguo. Number() lo convierte a NaN y || 2 garantiza el fallback. */
    function getNumWorkers() {
        const cores = Number(navigator.hardwareConcurrency) || 2;
        return Math.min(4, Math.max(1, Math.floor(cores / 2)));
    }

    /* ── Exponer inicio globalmente ─────────────────────────── */
    window.initQuagga = startScanner;

    /* ── Botones ───────────────────────────────────────────── */
    openModalButton.addEventListener('click', function () {
        modal.classList.remove('hidden');
        startScanner();
    });

    closeModalButton.addEventListener('click', function () {
        stopScanner();
        modal.classList.add('hidden');
    });

    if (closeResultModal) {
        closeResultModal.addEventListener('click', function () {
            resultModal.classList.add('hidden');
        });
    }

    /* ══════════════════════════════════════════════════════════
       INICIO DEL ESCÁNER
    ══════════════════════════════════════════════════════════ */
    function buildQuaggaConfig(useFrontCamera) {
        return {
            inputStream: {
                name   : 'Live',
                type   : 'LiveStream',
                target : document.querySelector('#interactive'),
                constraints: {
                    facingMode : useFrontCamera ? 'user' : 'environment',
                    // Subimos la resolución ideal — más píxeles = más detalle
                    // para distinguir barras finas. El min bajo (640x480)
                    // sigue permitiendo que funcione en cámaras más débiles;
                    // el navegador elige lo mejor disponible entre min y max.
                    width  : { min: 640, ideal: 1920, max: 1920 },
                    height : { min: 480, ideal: 1080, max: 1080 },
                },
                area: {
                    // Ajustamos el área para que coincida mejor con el recuadro verde de tu UI
                    top    : '20%',
                    right  : '5%',
                    left   : '5%',
                    bottom : '20%'
                },
                // singleChannel=false es lo correcto: le dice a Quagga que
                // convierta el frame RGB completo a escala de grises antes de
                // buscar bordes. Con singleChannel=true (como estaba antes)
                // Quagga asume que YA recibe un solo canal y toma uno crudo
                // de la imagen a color sin convertir — literalmente reduce el
                // contraste disponible para detectar barras, sobre todo con
                // luz de color (tubos fluorescentes, luz cálida de foco) o
                // reflejos. El comentario anterior decía que ayudaba en baja
                // iluminación; es al revés.
                singleChannel: false,
            },
            locator: {
                // 'large' en vez de 'medium': busca patrones de barra más
                // anchos, lo que ayuda con códigos algo borrosos o mal
                // enfocados — a costa de un poco de velocidad, aceptable
                // porque el problema reportado es precisión, no lentitud.
                patchSize  : 'large',
                // halfSample=false: procesa el frame a su resolución real en
                // vez de reducirlo a la mitad antes de buscar el código.
                // Con halfSample=true (como estaba) se pierde justo el detalle
                // fino que hace falta para leer barras delgadas con cámaras de
                // gama baja o con poca luz — es la causa más probable de que
                // el escáner "no se adapte" a distintas resoluciones/cámaras.
                halfSample : false,
            },
            numOfWorkers: getNumWorkers(),
            decoder: {
                readers  : ['ean_reader'],
                multiple : false,
            },
            locate: true,
        };
    }

    /* ── Aplicar constraints avanzadas de cámara (CRÍTICO) ──
       Se intenta aplicar focusMode y zoom DESPUÉS de iniciar Quagga,
       dentro de un try/catch. Si el navegador no lo soporta (Firefox,
       Safari antiguo), se ignora silenciosamente sin romper el escáner. */
    async function applyAdvancedCameraConstraints() {
        try {
            const video = document.querySelector('#interactive video');
            if (!video || !video.srcObject) return;

            const track = video.srcObject.getVideoTracks()[0];
            if (!track || typeof track.applyConstraints !== 'function') return;

            await track.applyConstraints({
                advanced: [
                    { focusMode: 'continuous' },
                    { exposureMode: 'continuous' },
                    { whiteBalanceMode: 'continuous' },
                ]
            });
        } catch (e) {
            /* Ignorado — el escáner funciona sin estas optimizaciones */
        }
    }

    function startScanner(useFrontCamera) {
        if (isScanning) return;

        voteMap = {};
        updateVoteBar(0);

        Quagga.init(buildQuaggaConfig(!!useFrontCamera), function (err) {
            if (err) {
                /* CRÍTICO — Fallback a cámara frontal si falla environment (Safari iOS) */
                if (!useFrontCamera &&
                    (err.name === 'OverconstrainedError' ||
                     err.name === 'NotReadableError' ||
                     (err.message && err.message.includes('constraint')))) {
                    setStatus('Reintentando con cámara frontal...', 'blue');
                    setTimeout(() => startScanner(true), 500);
                    return;
                }
                console.error('[Quagga init]', err);
                setStatus('❌ Sin acceso a la cámara', 'red');
                return;
            }

            Quagga.start();
            isScanning = true;
            setStatus('📷 Enfoque el código en el área central', 'black');
            resetStallTimer();

            /* Aplicar optimizaciones de cámara de forma asíncrona y segura */
            setTimeout(applyAdvancedCameraConstraints, 800);
        });

        /* ── Feedback visual (canvas overlay) ─────────────── */
        Quagga.onProcessed(function (result) {
            const ctx    = Quagga.canvas.ctx.overlay;
            const canvas = Quagga.canvas.dom.overlay;
            ctx.clearRect(0, 0, parseInt(canvas.getAttribute('width')), parseInt(canvas.getAttribute('height')));

            if (!result) return;

            if (result.boxes) {
                result.boxes
                    .filter(b => b !== result.box)
                    .forEach(b =>
                        Quagga.ImageDebug.drawPath(b, { x: 0, y: 1 }, ctx, { color: 'rgba(0,255,0,0.4)', lineWidth: 1 })
                    );
            }

            if (result.box) {
                Quagga.ImageDebug.drawPath(result.box, { x: 0, y: 1 }, ctx, { color: '#38bdf8', lineWidth: 2 });
            }

            if (result.codeResult?.code) {
                Quagga.ImageDebug.drawPath(result.line, { x: 'x', y: 'y' }, ctx, { color: '#ef4444', lineWidth: 3 });
            }
        });

        /* ── Detección: sistema de votos ───────────────────── */
        Quagga.onDetected(function (result) {
            const code = result.codeResult?.code;
            if (!code) return;

            // Cualquier lectura, válida o no, prueba que la cámara SÍ está
            // viendo un patrón de barras — reiniciamos los avisos de "no veo nada".
            resetStallTimer();

            if (!validateEAN13(code)) return;

            const now = Date.now();
            if (now - lastScanTime < 2000) return;

            voteMap[code] = (voteMap[code] || 0) + 1;

            Object.keys(voteMap).forEach(k => {
                if (k !== code) delete voteMap[k];
            });

            const votes = voteMap[code];
            updateVoteBar(votes);

            if (votes < VOTES_REQUIRED) {
                setStatus(`🔍 Leyendo… (${votes}/${VOTES_REQUIRED})`, 'blue');
                return;
            }

            lastScanTime = now;
            voteMap = {};
            updateVoteBar(0);

            beepSound.play().catch(() => {});
            setStatus('✅ ¡Código detectado! Consultando...', 'green');
            stopScanner();
            fetchProduct(code);
        });
    }

    /* ── Detener escáner ───────────────────────────────────── */
    function stopScanner() {
        if (!isScanning) return;
        Quagga.stop();
        isScanning = false;
        clearStallTimer();

        const canvas = document.querySelector('#interactive canvas');
        if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    }

    /* ── Barra de votos ────────────────────────────────────── */
    function updateVoteBar(votes) {
        if (!voteBar) return;
        const pct = Math.min((votes / VOTES_REQUIRED) * 100, 100);
        voteBar.style.width = pct + '%';

        if (voteLabel) {
            voteLabel.textContent = votes > 0 ? `Confirmando… ${votes}/${VOTES_REQUIRED}` : '';
        }
    }

    /* ── Estado del escáner ────────────────────────────────── */
    function setStatus(text, color) {
        if (!scanningStatus) return;
        scanningStatus.textContent = text;
        scanningStatus.className = 'text-center mt-4 font-semibold text-white min-h-6 z-50 px-4 py-2 rounded-full ';
        const colorMap = {
            black : 'bg-black bg-opacity-50',
            blue  : 'bg-blue-600 bg-opacity-90',
            green : 'bg-green-600 bg-opacity-90',
            red   : 'bg-red-600 bg-opacity-90',
        };
        scanningStatus.className += colorMap[color] || colorMap.black;
    }

    /* ── Validación matemática EAN-13 ──────────────────────── */
    function validateEAN13(barcode) {
        if (barcode.length !== 13 || isNaN(barcode)) return false;
        let sum = 0;
        for (let i = 0; i < 12; i++) {
            const d = parseInt(barcode[i]);
            sum += i % 2 === 0 ? d : d * 3;
        }
        return (10 - (sum % 10)) % 10 === parseInt(barcode[12]);
    }

    /* ── Consulta al servidor ──────────────────────────────── */
    function fetchProduct(barcode) {
        const formData = new FormData();
        formData.append('barcode', barcode);

        fetch('/scan_barcode/', {
            method  : 'POST',
            headers : { 'X-CSRFToken': getCookie('csrftoken') },
            body    : formData,
        })
        .then(r => r.json())
        .then(data => {
            modal.classList.add('hidden');
            resultModal.classList.remove('hidden');
            displayResult(data);
            setStatus('📷 Enfoque el código en el área central', 'black');
        })
        .catch(error => {
            console.error('[fetchProduct]', error);
            setStatus('❌ Error de red. Intente de nuevo.', 'red');
            setTimeout(startScanner, 2500);
        });
    }

    /* ── Mostrar resultado ─────────────────────────────────── */
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
                        </div>` : ''}
                    </div>
                </div>`;
        } else {
            resultContent.innerHTML = `
                <div class="text-center py-8 animate-fade-in">
                    <div class="bg-red-100 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-4 animate-bounce">
                        <i class='bx bx-error text-5xl text-red-500'></i>
                    </div>
                    <h4 class="text-2xl font-bold text-gray-800 mb-2">¡Ups!</h4>
                    <p class="text-gray-600 mb-6 px-4">${data.error || 'El producto no está registrado o sin stock.'}</p>
                    <div class="inline-block bg-gray-100 px-4 py-2 rounded-lg border border-gray-300">
                        <span class="text-xs text-gray-500 block">Código leído:</span>
                        <span class="font-mono font-bold text-gray-700 tracking-wider">${data.barcode}</span>
                    </div>
                </div>`;
        }
    }

    /* ── Helper: leer cookie CSRF ──────────────────────────── */
    function getCookie(name) {
        let value = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(c => {
                const [k, v] = c.trim().split('=');
                if (k === name) value = decodeURIComponent(v);
            });
        }
        return value;
    }
});