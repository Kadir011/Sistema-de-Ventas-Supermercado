document.addEventListener("DOMContentLoaded", () => {
    const chatbotButton = document.getElementById("chatbot-button");
    const chatbotModal = document.getElementById("chatbot-modal");
    const closeChatbot = document.getElementById("close-chatbot");
    const sendMessage = document.getElementById("send-message");
    const chatInput = document.getElementById("chat-input");
    const messageContainer = document.getElementById("message-container");

    // Variable para rastrear si el usuario está autenticado (para el escáner de códigos de barras)
    let userIsAuthenticated = false; // Cambia a true cuando el usuario inicie sesión

    chatbotButton.addEventListener("click", () => {
        chatbotModal.classList.toggle("hidden");
    });

    closeChatbot.addEventListener("click", () => {
        chatbotModal.classList.add("hidden");
    });

    sendMessage.addEventListener("click", async () => {
        const userMessage = chatInput.value;
        if (userMessage.trim() === "") return;

        displayMessage(userMessage, "user");
        chatInput.value = ""; // Limpiar campo de entrada

        const response = await sendToAPI(userMessage);
        displayMessage(response, "bot");
    });

    function displayMessage(message, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("mb-2", sender === "user" ? "text-right" : "text-left");
        messageDiv.textContent = message;
        messageContainer.appendChild(messageDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight; // Auto-scroll al último mensaje
    }

    async function sendToAPI(message) {
        const apiKey = "e898e67048f9c6208c24f812ebc3c5ea66f75710"; // API key proporcionada por Magic Loops
        const url = "https://magicloops.dev/api/loop/2e97e4bb-a5fc-4393-899f-91d84e9c8ed1/run"; // Endpoint proporcionado por Magic Loops

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${apiKey}`, // Asumiendo que requiere autenticación con Bearer
                },
                body: JSON.stringify({
                    query: message, // Enviar el mensaje del usuario como "query"
                    isAuthenticated: userIsAuthenticated // Indicar si el usuario está autenticado (para el escáner)
                }),
            });

            if (!response.ok) {
                console.log("Estado de la respuesta:", response.status, response.statusText);
                throw new Error(`Error al conectar con la API: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Respuesta completa de la API:", data); // Para depurar
            // Ajusta según la estructura real de la respuesta de Magic Loops
            return data.response || data.message || data.output || "Lo siento, no pude obtener una respuesta.";
        } catch (error) {
            console.error("Error detallado:", error);
            return `Lo siento, no pude obtener una respuesta. Error: ${error.message}. Intenta nuevamente más tarde.`;
        }
    }
}); 









