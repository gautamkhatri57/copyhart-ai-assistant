const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");


function addMessage(message, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);

    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


async function sendMessage() {

    const question = messageInput.value.trim();

    if (!question) {
        return;
    }


    // Show user message
    addMessage(question, "user");

    // Clear input
    messageInput.value = "";

    // Disable button
    sendButton.disabled = true;


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


        // Show bot response
        addMessage(data.answer, "bot");


    } catch (error) {

        console.error(error);

        addMessage(
            "Sorry, something went wrong. Please try again.",
            "bot"
        );

    }


    sendButton.disabled = false;

    messageInput.focus();
}


// Send button
sendButton.addEventListener("click", sendMessage);


// Enter key
messageInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

    }

});