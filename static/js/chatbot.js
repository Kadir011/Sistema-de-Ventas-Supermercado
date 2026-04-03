/**
 * chatbot.js — Asistente virtual My Supermarket
 *
 * Persistencia del historial:
 * - Se usa localStorage con una clave que incluye el rol/usuario,
 *   así el historial sobrevive navegaciones entre páginas (full page reload).
 * - sessionStorage se pierde en cada navegación en Django (MPA).
 * - El historial se limpia automáticamente al cerrar sesión (logout).
 */

document.addEventListener("DOMContentLoaded", () => {

    /* ── Clave de storage basada en el usuario actual ────────────── */
    const userRole = (typeof CHATBOT_USER_ROLE !== "undefined") ? CHATBOT_USER_ROLE : "guest";
    const userName = (typeof CHATBOT_USER_NAME !== "undefined") ? CHATBOT_USER_NAME : "guest";
    // Clave única por usuario: si cambia de sesión, usa un espacio diferente
    const STORAGE_PREFIX   = `chatbot_${userRole}_${userName.replace(/\s+/g, '_')}`;
    const KEY_HISTORY      = `${STORAGE_PREFIX}_history`;
    const KEY_MESSAGES     = `${STORAGE_PREFIX}_messages`;
    const KEY_WELCOME      = `${STORAGE_PREFIX}_welcome`;

    /* ── Elementos del DOM ───────────────────────────────────────── */
    const chatbotButton    = document.getElementById("chatbot-button");
    const chatbotModal     = document.getElementById("chatbot-modal");
    const closeChatbot     = document.getElementById("close-chatbot");
    const sendMessage      = document.getElementById("send-message");
    const chatInput        = document.getElementById("chat-input");
    const messageContainer = document.getElementById("message-container");

    if (!chatbotButton || !chatbotModal) return;

    /* ── Helpers de storage (con fallback silencioso) ────────────── */
    function storageGet(key) {
        try { return localStorage.getItem(key); } catch (_) { return null; }
    }
    function storageSet(key, value) {
        try { localStorage.setItem(key, value); } catch (_) {}
    }

    /* ── Recuperar estado previo ─────────────────────────────────── */
    let conversationHistory = [];
    let welcomeShown        = storageGet(KEY_WELCOME) === "true";

    try {
        const raw = storageGet(KEY_HISTORY);
        if (raw) conversationHistory = JSON.parse(raw);
    } catch (_) {}

    /* ── Persistir historial de conversación ─────────────────────── */
    function persistHistory() {
        storageSet(KEY_HISTORY, JSON.stringify(conversationHistory));
    }

    /* ── Persistir burbujas renderizadas ─────────────────────────── */
    function persistMessage(text, sender) {
        try {
            const raw = storageGet(KEY_MESSAGES);
            const messages = raw ? JSON.parse(raw) : [];
            messages.push({ text, sender });
            // Máximo 60 burbujas almacenadas
            if (messages.length > 60) messages.splice(0, messages.length - 60);
            storageSet(KEY_MESSAGES, JSON.stringify(messages));
        } catch (_) {}
    }

    /* ── Restaurar burbujas en el DOM ────────────────────────────── */
    function restoreMessages() {
        try {
            const raw = storageGet(KEY_MESSAGES);
            if (!raw) return;
            const messages = JSON.parse(raw);
            messages.forEach(({ text, sender }) => _renderBubble(text, sender));
            scrollToBottom();
        } catch (_) {}
    }

    /* ── Saludo inicial personalizado ────────────────────────────── */
    function buildWelcomeMessage() {
        if (userRole === "guest") {
            return ("¡Hola, Invitado! 👋 Soy tu asistente de My Supermarket. "
                  + "Puedo ayudarte con información de productos, precios y métodos de pago. "
                  + "Regístrate para poder comprar. ¿En qué te puedo ayudar?");
        } else if (userRole === "admin") {
            return (`¡Hola, ${userName}! 👋 Bienvenido al panel de My Supermarket. `
                  + "¿En qué te puedo ayudar hoy?");
        } else {
            return (`¡Hola, ${userName}! 👋 Bienvenido a My Supermarket. `
                  + "Puedo ayudarte con productos, precios y tu carrito de compras. "
                  + "¿En qué te puedo ayudar?");
        }
    }

    /* ── Abrir / cerrar modal ────────────────────────────────────── */
    chatbotButton.addEventListener("click", () => {
        chatbotModal.classList.toggle("hidden");

        if (!chatbotModal.classList.contains("hidden")) {
            chatInput.focus();

            if (messageContainer.children.length === 0) {
                // El DOM está vacío (navegación a nueva página o primera vez)
                if (!welcomeShown) {
                    // Primera vez en toda la sesión: mostrar saludo
                    welcomeShown = true;
                    storageSet(KEY_WELCOME, "true");
                    displayMessage(buildWelcomeMessage(), "bot");
                } else {
                    // Ya había mensajes previos: restaurarlos desde storage
                    restoreMessages();
                }
            }
            // Si el contenedor ya tiene hijos (modal cerrado y reabierto
            // sin navegar), no hacemos nada: los mensajes ya están ahí.

            scrollToBottom();
        }
    });

    closeChatbot.addEventListener("click", () => {
        chatbotModal.classList.add("hidden");
    });

    /* ── Envío de mensajes ───────────────────────────────────────── */
    sendMessage.addEventListener("click", processMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            processMessage();
        }
    });

    async function processMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

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

    /* ── Llamada al backend ──────────────────────────────────────── */
    async function sendToBackend(userMessage) {
        try {
            const csrf = getCookie("csrftoken") || "";
            const headers = { "Content-Type": "application/json" };
            if (csrf) headers["X-CSRFToken"] = csrf;

            const response = await fetch("/chatbot/api/", {
                method: "POST",
                headers,
                body: JSON.stringify({
                    message: userMessage,
                    history: conversationHistory,
                }),
            });

            const contentType = response.headers.get("content-type") || "";
            if (!contentType.includes("application/json")) {
                console.error("[Chatbot] Respuesta no es JSON. Status:", response.status);
                return "⚠️ El asistente no está disponible en este momento. Intenta más tarde.";
            }

            const data = await response.json();

            if (data.error) {
                console.warn("[Chatbot] Error del backend:", data.error);
                return "⚠️ " + data.error;
            }

            const botReply = data.reply || "No obtuve respuesta.";

            // Actualizar historial y persistirlo
            conversationHistory.push({ role: "user",  content: userMessage });
            conversationHistory.push({ role: "model", content: botReply   });

            // Máximo 80 entradas (40 turnos de conversación)
            if (conversationHistory.length > 80) {
                conversationHistory = conversationHistory.slice(-80);
            }

            persistHistory();
            return botReply;

        } catch (err) {
            console.error("[Chatbot] Error de red:", err);
            return "⚠️ Error de conexión. Revisa tu internet e inténtalo de nuevo.";
        }
    }

    /* ── Renderizado ─────────────────────────────────────────────── */
    function displayMessage(text, sender) {
        _renderBubble(text, sender);
        persistMessage(text, sender);
        scrollToBottom();
    }

    function _renderBubble(text, sender) {
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

    /* ── Helpers ─────────────────────────────────────────────────── */
    function markdownToHtml(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g,     "<em>$1</em>")
            .replace(/\n\n/g, "</p><p class='mt-2'>")
            .replace(/\n/g,   "<br>");
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