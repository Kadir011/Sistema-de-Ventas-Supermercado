document.addEventListener("DOMContentLoaded", () => {
    console.log("Chatbot cargado — universal (invitados, clientes y admins).");

    /* ── Elementos del DOM ───────────────────────────────────────── */
    const chatbotButton    = document.getElementById("chatbot-button");
    const chatbotModal     = document.getElementById("chatbot-modal");
    const closeChatbot     = document.getElementById("close-chatbot");
    const sendMessage      = document.getElementById("send-message");
    const chatInput        = document.getElementById("chat-input");
    const messageContainer = document.getElementById("message-container");

    if (!chatbotButton || !chatbotModal) return;

    /* ── Historial en memoria ────────────────────────────────────── */
    let conversationHistory = [];

    /* ── Abrir / cerrar modal ────────────────────────────────────── */
    chatbotButton.addEventListener("click", () => {
        chatbotModal.classList.toggle("hidden");
        if (!chatbotModal.classList.contains("hidden")) {
            chatInput.focus();
            if (conversationHistory.length === 0) {
                displayMessage(
                    "¡Hola! 👋 Soy tu asistente de My Supermarket. " +
                    "Puedo ayudarte con información de productos, precios y métodos de pago. " +
                    "¿En qué te puedo ayudar hoy?",
                    "bot"
                );
            }
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
            // Obtener CSRF token — puede no existir para invitados
            const csrf = getCookie("csrftoken") || "";

            const headers = { "Content-Type": "application/json" };
            if (csrf) headers["X-CSRFToken"] = csrf;

            const response = await fetch("/chatbot/api/", {
                method: "POST",
                headers: headers,
                body: JSON.stringify({
                    message: userMessage,
                    history: conversationHistory,
                }),
            });

            // Si la respuesta no es JSON, capturarlo limpiamente
            const contentType = response.headers.get("content-type") || "";
            if (!contentType.includes("application/json")) {
                console.error("[Chatbot] Respuesta no es JSON. Status:", response.status);
                return "⚠️ El asistente no está disponible en este momento. Intenta más tarde.";
            }

            const data = await response.json();

            if (data.error) {
                console.error("[Chatbot] Error del servidor:", data.error);
                return "⚠️ El asistente tiene un problema técnico. Inténtalo de nuevo.";
            }

            const botReply = data.reply || "No obtuve respuesta.";

            conversationHistory.push({ role: "user",  content: userMessage });
            conversationHistory.push({ role: "model", content: botReply   });

            // Mantener máximo 40 turnos
            if (conversationHistory.length > 40) {
                conversationHistory = conversationHistory.slice(-40);
            }

            return botReply;

        } catch (err) {
            console.error("[Chatbot] Error de red:", err);
            return "⚠️ Error de conexión. Revisa tu internet e inténtalo de nuevo.";
        }
    }

    /* ── Renderizado de mensajes ─────────────────────────────────── */
    function displayMessage(text, sender) {
        const wrap = document.createElement("div");
        wrap.classList.add("mb-3", "flex");

        const bubble = document.createElement("div");
        bubble.classList.add(
            "p-3", "rounded-lg", "max-w-[85%]", "text-sm", "leading-relaxed"
        );

        if (sender === "user") {
            wrap.classList.add("justify-end");
            bubble.classList.add("bg-green-100", "text-green-800");
            bubble.textContent = text;
        } else {
            wrap.classList.add("justify-start");
            bubble.classList.add(
                "bg-white", "text-gray-800", "shadow-sm",
                "border", "border-gray-100"
            );
            bubble.innerHTML = markdownToHtml(text);
        }

        wrap.appendChild(bubble);
        messageContainer.appendChild(wrap);
        scrollToBottom();
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