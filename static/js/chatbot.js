document.addEventListener("DOMContentLoaded", () => {
    const chatbotButton = document.getElementById("chatbot-button");
    const chatbotModal = document.getElementById("chatbot-modal");
    const closeChatbot = document.getElementById("close-chatbot");
    const sendMessage = document.getElementById("send-message");
    const chatInput = document.getElementById("chat-input");
    const messageContainer = document.getElementById("message-container");

    chatbotButton.addEventListener("click", () => {
        chatbotModal.classList.toggle("hidden");
        chatInput.focus();
    });

    closeChatbot.addEventListener("click", () => {
        chatbotModal.classList.add("hidden");
    });

    // Función para obtener el token CSRF de las cookies (Seguridad Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    sendMessage.addEventListener("click", processMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") processMessage();
    });

    async function processMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        displayMessage(userMessage, "user");
        chatInput.value = "";

        // Mostrar un pequeño indicador de carga
        const loadingDiv = document.createElement("div");
        loadingDiv.id = "bot-loading";
        loadingDiv.className = "text-left text-gray-400 italic text-xs mb-2";
        loadingDiv.textContent = "Escribiendo...";
        messageContainer.appendChild(loadingDiv);

        const response = await sendToGemini(userMessage);
        
        // Quitar indicador de carga y mostrar respuesta
        const loader = document.getElementById("bot-loading");
        if(loader) loader.remove();
        displayMessage(response, "bot");
    }

    function displayMessage(message, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("mb-3", "p-2", "rounded-lg", "max-w-[80%]", "text-sm");
        
        if (sender === "user") {
            messageDiv.classList.add("ml-auto", "bg-green-100", "text-green-800");
        } else {
            messageDiv.classList.add("bg-gray-200", "text-gray-800");
        }
        
        messageDiv.textContent = message;
        messageContainer.appendChild(messageDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    async function sendToGemini(message) {
        try {
            const response = await fetch('/chatbot/api/', { // Tu endpoint de Django
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie('csrftoken'),
                },
                body: JSON.stringify({ message: message }),
            });

            const data = await response.json();
            return data.reply || data.error || "Lo siento, hubo un problema técnico.";
        } catch (error) {
            console.error("Error:", error);
            return "Error de conexión. Intenta más tarde.";
        }
    }
});