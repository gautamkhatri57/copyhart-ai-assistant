const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatbotToggle = document.getElementById("chatbot-toggle");
const chatbot = document.getElementById("chatbot");

chatbotToggle.addEventListener("click", function () {
    if (chatbot.style.display === "flex") {
        chatbot.style.display = "none";
    } else {
        chatbot.style.display = "flex";
        messageInput.focus();
    }
});

function addMessage(message, sender) {
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);
    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    return messageDiv;
}

function showTyping() {
    const typingDiv = document.createElement("div");

    typingDiv.classList.add(
        "message",
        "bot",
        "typing-message"
    );

    typingDiv.innerHTML = `
        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    return typingDiv;
}

async function sendMessage() {
    const question = messageInput.value.trim();

    if (!question) {
        return;
    }

    addMessage(question, "user");

    messageInput.value = "";

    sendButton.disabled = true;
    messageInput.disabled = true;

    const typingMessage = showTyping();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        typingMessage.remove();

        addMessage(data.answer, "bot");

    } catch (error) {
        console.error(error);

        typingMessage.remove();

        addMessage(
            "Sorry, something went wrong. Please try again.",
            "bot"
        );

    } finally {
        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});