/**
 * chatbot.js — Asistente virtual My Supermarket
 * v2.0 — Diferenciación completa por rol (admin / customer / guest)
 *
 * Mejoras:
 * - Resumen ejecutivo al abrir (admin: KPIs + alertas; cliente: historial)
 * - Botones de acción rápida contextuales por rol
 * - Burbujas de bienvenida diferenciadas
 * - Persistencia por usuario en localStorage
 */

document.addEventListener("DOMContentLoaded", () => {

    /* ── Contexto del usuario ─────────────────────────────────── */
    const userRole = (typeof CHATBOT_USER_ROLE !== "undefined") ? CHATBOT_USER_ROLE : "guest";
    const userName = (typeof CHATBOT_USER_NAME !== "undefined") ? CHATBOT_USER_NAME : "Invitado";

    const STORAGE_PREFIX = `chatbot_${userRole}_${userName.replace(/\s+/g, '_')}`;
    const KEY_HISTORY = `${STORAGE_PREFIX}_history`;
    const KEY_MESSAGES = `${STORAGE_PREFIX}_messages`;
    const KEY_WELCOME = `${STORAGE_PREFIX}_welcome`;

    /* ── Elementos DOM ───────────────────────────────────────── */
    const chatbotButton = document.getElementById("chatbot-button");
    const chatbotModal = document.getElementById("chatbot-modal");
    const closeChatbot = document.getElementById("close-chatbot");
    const sendMessage = document.getElementById("send-message");
    const chatInput = document.getElementById("chat-input");
    const messageContainer = document.getElementById("message-container");

    if (!chatbotButton || !chatbotModal) return;

    /* ── Storage helpers ─────────────────────────────────────── */
    const storageGet = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
    const storageSet = (k, v) => { try { localStorage.setItem(k, v); } catch { } };

    let conversationHistory = [];
    let welcomeShown = storageGet(KEY_WELCOME) === "true";

    try {
        const raw = storageGet(KEY_HISTORY);
        if (raw) conversationHistory = JSON.parse(raw);
    } catch { }

    function persistHistory() {
        storageSet(KEY_HISTORY, JSON.stringify(conversationHistory));
    }

    function persistMessage(text, sender, type = 'text') {
        try {
            const raw = storageGet(KEY_MESSAGES);
            const msgs = raw ? JSON.parse(raw) : [];
            msgs.push({ text, sender, type });
            if (msgs.length > 80) msgs.splice(0, msgs.length - 80);
            storageSet(KEY_MESSAGES, JSON.stringify(msgs));
        } catch { }
    }

    function restoreMessages() {
        try {
            const raw = storageGet(KEY_MESSAGES);
            if (!raw) return;
            JSON.parse(raw).forEach(({ text, sender, type }) => _renderBubble(text, sender, type));
            scrollToBottom();
        } catch { }
    }

    /* ── Configuración de acciones rápidas por rol ───────────── */
    const QUICK_ACTIONS = {
        admin: [
            { label: "📊 Ventas de hoy", prompt: "¿Cuántas ventas y cuánto se recaudó hoy?" },
            { label: "⚠️ Alertas de stock", prompt: "¿Qué productos tienen stock crítico o están agotados?" },
            { label: "📈 Resumen ejecutivo", prompt: "Dame un resumen ejecutivo del negocio" },
            { label: "🏆 Top productos (30 días)", prompt: "¿Cuáles son los productos más vendidos este mes?" },
            { label: "🗂️ Ir a Reportes", prompt: "Quiero ver los reportes del sistema. ¿Cómo llego?" },
            { label: "📦 Productos con poco stock", prompt: "Lista los 5 productos con menos stock disponible" },
        ],
        customer: [
            { label: "🛒 Ver tienda", prompt: "¿Cómo entro a la tienda para comprar?" },
            { label: "🔍 Buscar producto", prompt: "Ayúdame a buscar un producto" },
            { label: "💳 Métodos de pago", prompt: "¿Qué métodos de pago aceptan?" },
            { label: "📄 Mis compras", prompt: "¿Cómo veo mis compras anteriores y descargo mis facturas?" },
            { label: "🏷️ Precios y descuentos", prompt: "¿Cómo funcionan los descuentos? ¿Mis precios incluyen IVA?" },
            { label: "📷 Escáner de productos", prompt: "¿Puedo escanear un código de barras para ver el precio?" },
        ],
        guest: [
            { label: "🎁 ¿Qué ofrecen?", prompt: "¿Qué productos y marcas tienen disponibles?" },
            { label: "📝 ¿Cómo me registro?", prompt: "¿Cómo creo una cuenta para comprar?" },
            { label: "💰 ¿Cómo son los precios?", prompt: "¿Los precios incluyen IVA? ¿Tienen descuentos?" },
            { label: "💳 Formas de pago", prompt: "¿Qué métodos de pago aceptan?" },
            { label: "📦 Proceso de compra", prompt: "¿Cómo funciona el proceso de compra?" },
            { label: "🔒 ¿Es seguro comprar?", prompt: "¿Es seguro comprar aquí? ¿Protegen mis datos?" },
        ],
    };

    /* ── Resumen ejecutivo por rol ───────────────────────────── */
    async function fetchQuickSummary() {
        try {
            const csrf = getCookie("csrftoken") || "";
            const res = await fetch('/chatbot/summary/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    ...(csrf ? { 'X-CSRFToken': csrf } : {}),
                },
            });
            if (!res.ok) return null;
            const data = await res.json();
            // Si el servidor responde como guest pero el rol local es customer/admin,
            // significa que la sesión no viajó — devolver null para no mostrar nada
            if (data.role === 'guest' && userRole !== 'guest') return null;
            return data;
        } catch { return null; }
    }

    function buildAdminSummaryHTML(data) {
        const alerts = [];
        if (data.out_of_stock > 0) alerts.push(`<span class="alert-chip red">⚠️ ${data.out_of_stock} agotados</span>`);
        if (data.low_stock_count > 0) alerts.push(`<span class="alert-chip amber">📦 ${data.low_stock_count} stock crítico</span>`);

        return `
        <div class="exec-summary">
            <div class="exec-title">📊 Resumen ejecutivo</div>
            <div class="exec-kpis">
                <div class="exec-kpi">
                    <span class="kpi-num">${data.count_24h}</span>
                    <span class="kpi-label">Ventas hoy</span>
                </div>
                <div class="exec-kpi">
                    <span class="kpi-num">$${data.total_24h.toFixed(2)}</span>
                    <span class="kpi-label">Recaudado hoy</span>
                </div>
                <div class="exec-kpi">
                    <span class="kpi-num">$${data.total_7d.toFixed(2)}</span>
                    <span class="kpi-label">Esta semana</span>
                </div>
            </div>
            ${alerts.length ? `<div class="exec-alerts">${alerts.join('')}</div>` : ''}
        </div>`;
    }

    function buildCustomerSummaryHTML(data) {
        if (!data.order_count) return '';
        return `
        <div class="exec-summary customer">
            <div class="exec-title">👤 Tu cuenta</div>
            <div class="exec-kpis">
                <div class="exec-kpi">
                    <span class="kpi-num">${data.order_count}</span>
                    <span class="kpi-label">Compras</span>
                </div>
                <div class="exec-kpi">
                    <span class="kpi-num">$${data.total_spent.toFixed(2)}</span>
                    <span class="kpi-label">Total gastado</span>
                </div>
                ${data.last_order_date ? `<div class="exec-kpi"><span class="kpi-num" style="font-size:0.75rem;">${data.last_order_date}</span><span class="kpi-label">Última compra</span></div>` : ''}
            </div>
        </div>`;
    }

    /* ── Mensajes de bienvenida ───────────────────────────────── */
    function getWelcomeText() {
        if (userRole === 'admin') {
            return `¡Hola, ${userName}! 👋 Soy tu asistente de gestión.\n\nPuedes preguntarme sobre ventas, stock, métricas del negocio o pedirme que te guíe a cualquier sección del panel.`;
        }
        if (userRole === 'customer') {
            return `¡Hola, ${userName}! 👋 Soy tu asistente de compras.\n\nPuedo ayudarte a encontrar productos, conocer precios, guiarte en el proceso de compra o consultar tus pedidos anteriores.`;
        }
        return `¡Hola! 👋 Bienvenido a My Supermarket.\n\nExplora nuestro catálogo, conoce nuestros productos y regístrate gratis para empezar a comprar. ¿En qué te puedo ayudar?`;
    }

    /* ── Renderizado de botones de acción rápida ─────────────── */
    function renderQuickActions() {
        const actions = QUICK_ACTIONS[userRole] || QUICK_ACTIONS.guest;
        const wrap = document.createElement('div');
        wrap.className = 'quick-actions-wrap';
        wrap.innerHTML = `<p class="qa-label">Acciones rápidas:</p>`;

        const grid = document.createElement('div');
        grid.className = 'qa-grid';

        actions.forEach(({ label, prompt }) => {
            const btn = document.createElement('button');
            btn.className = 'qa-btn';
            btn.textContent = label;
            btn.addEventListener('click', () => {
                // Remover los botones tras el primer uso
                wrap.remove();
                chatInput.value = prompt;
                processMessage();
            });
            grid.appendChild(btn);
        });

        wrap.appendChild(grid);
        messageContainer.appendChild(wrap);
    }

    /* ── Apertura del modal ──────────────────────────────────── */
    chatbotButton.addEventListener("click", async () => {
        chatbotModal.classList.toggle("hidden");

        if (chatbotModal.classList.contains("hidden")) return;

        chatInput.focus();

        if (messageContainer.children.length === 0) {
            if (!welcomeShown) {
                welcomeShown = true;
                storageSet(KEY_WELCOME, "true");

                // Mensaje de bienvenida
                displayMessage(getWelcomeText(), "bot");

                // Resumen ejecutivo para admin y customer
                if (userRole === 'admin' || userRole === 'customer') {
                    const summary = await fetchQuickSummary();
                    if (summary && summary.data && summary.role === userRole && Object.keys(summary.data).length > 0) {
                        const html = userRole === 'admin'
                            ? buildAdminSummaryHTML(summary.data)
                            : buildCustomerSummaryHTML(summary.data);
                        if (html) {
                            const el = document.createElement('div');
                            el.className = 'mb-3';
                            el.innerHTML = html;
                            messageContainer.appendChild(el);
                        }
                    }
                }

                // Botones de acción rápida
                renderQuickActions();
                scrollToBottom();
            } else {
                restoreMessages();
            }
        }

        scrollToBottom();
    });

    closeChatbot.addEventListener("click", () => chatbotModal.classList.add("hidden"));

    /* ── Envío de mensajes ───────────────────────────────────── */
    sendMessage.addEventListener("click", processMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); processMessage(); }
    });

    async function processMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        // Remover botones de acción rápida si aún están visibles
        const qa = messageContainer.querySelector('.quick-actions-wrap');
        if (qa) qa.remove();

        displayMessage(userMessage, "user");
        chatInput.value = "";
        chatInput.disabled = true;
        sendMessage.disabled = true;

        const loadingEl = createLoadingIndicator();
        messageContainer.appendChild(loadingEl);
        scrollToBottom();

        const reply = await sendToBackend(userMessage);
        loadingEl.remove();
        displayMessage(reply, "bot");

        chatInput.disabled = false;
        sendMessage.disabled = false;
        chatInput.focus();
    }

    /* ── Backend ────────────────────────────────────────────── */
    async function sendToBackend(userMessage) {
        try {
            const csrf = getCookie("csrftoken") || "";
            const response = await fetch("/chatbot/api/", {
                method: "POST",
                headers: { "Content-Type": "application/json", ...(csrf ? { "X-CSRFToken": csrf } : {}) },
                body: JSON.stringify({ message: userMessage, history: conversationHistory }),
            });

            if (!response.headers.get("content-type")?.includes("application/json")) {
                return "⚠️ El asistente no está disponible en este momento.";
            }

            const data = await response.json();
            if (data.error) return "⚠️ " + data.error;

            const botReply = data.reply || "No obtuve respuesta.";

            conversationHistory.push({ role: "user", content: userMessage });
            conversationHistory.push({ role: "model", content: botReply });
            if (conversationHistory.length > 80) conversationHistory = conversationHistory.slice(-80);
            persistHistory();

            return botReply;

        } catch {
            return "⚠️ Error de conexión. Revisa tu internet.";
        }
    }

    /* ── Renderizado de burbujas ─────────────────────────────── */
    function displayMessage(text, sender, type = 'text') {
        _renderBubble(text, sender, type);
        persistMessage(text, sender, type);
        scrollToBottom();
    }

    function _renderBubble(text, sender, type = 'text') {
        const wrap = document.createElement("div");
        wrap.classList.add("mb-3", "flex");

        const bubble = document.createElement("div");
        bubble.classList.add("p-3", "rounded-lg", "max-w-[85%]", "text-sm", "leading-relaxed");

        if (sender === "user") {
            wrap.classList.add("justify-end");
            bubble.classList.add("bg-green-100", "text-green-800");
            bubble.textContent = text;
        } else {
            wrap.classList.add("justify-start");
            bubble.classList.add("bg-white", "text-gray-800", "shadow-sm", "border", "border-gray-100");
            bubble.innerHTML = markdownToHtml(text);
        }

        wrap.appendChild(bubble);
        messageContainer.appendChild(wrap);
    }

    function createLoadingIndicator() {
        const el = document.createElement("div");
        el.className = "mb-3 flex justify-start";
        el.innerHTML = `
            <div class="bg-white border border-gray-100 shadow-sm p-3 rounded-lg text-sm text-gray-400 italic flex items-center gap-2">
                <span class="inline-flex gap-1">
                    <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0s"></span>
                    <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:.15s"></span>
                    <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:.3s"></span>
                </span>
                Escribiendo…
            </div>`;
        return el;
    }

    /* ── Helpers ────────────────────────────────────────────── */
    function markdownToHtml(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/\n\n/g, "</p><p class='mt-2'>")
            .replace(/\n/g, "<br>");
    }

    function scrollToBottom() {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function getCookie(name) {
        if (!document.cookie) return null;
        for (const c of document.cookie.split(";")) {
            const [k, v] = c.trim().split("=");
            if (k === name) return decodeURIComponent(v);
        }
        return null;
    }
});