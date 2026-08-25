
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="CopyHart AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# FastAPI backend URL
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

html_code = f"""
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

* {{
    box-sizing: border-box;
}}

html, body {{
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    font-family: Arial, sans-serif;
    background: transparent;
}}

#chatbot-toggle {{
    position: fixed;
    right: 25px;
    bottom: 25px;

    width: 60px;
    height: 60px;

    border: none;
    border-radius: 50%;

    background: #111827;
    color: white;

    font-size: 28px;
    cursor: pointer;

    z-index: 9999;

    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.25);

    display: flex;
    align-items: center;
    justify-content: center;
}}

#chatbot-toggle:hover {{
    background: #374151;
}}

.chat-container {{
    position: fixed;

    right: 25px;
    bottom: 95px;

    width: 380px;
    height: 550px;

    background: white;

    border-radius: 15px;

    box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);

    display: none;
    flex-direction: column;

    overflow: hidden;

    z-index: 9998;
}}

.chat-container h1 {{
    margin: 0;
    padding: 16px 16px 5px;

    background: #111827;
    color: white;

    text-align: center;

    font-size: 18px;
}}

.chat-container > p {{
    margin: 0;
    padding: 0 16px 16px;

    background: #111827;
    color: white;

    text-align: center;

    font-size: 12px;

    opacity: 0.8;
}}

#chat-box {{
    flex: 1;

    padding: 15px;

    overflow-y: auto;

    background: #f9fafb;
}}

.message {{
    max-width: 80%;

    padding: 10px 13px;

    margin-bottom: 10px;

    border-radius: 12px;

    font-size: 14px;

    line-height: 1.5;

    white-space: pre-wrap;

    word-wrap: break-word;
}}

.message.user {{
    margin-left: auto;

    background: #111827;
    color: white;

    border-bottom-right-radius: 3px;
}}

.message.bot {{
    margin-right: auto;

    background: #e5e7eb;
    color: #111827;

    border-bottom-left-radius: 3px;
}}

.input-area {{
    display: flex;

    align-items: center;

    padding: 8px 10px;

    border-top: 1px solid #ddd;

    background: white;
}}

#message-input {{
    flex: 1;

    height: 38px;

    padding: 8px 10px;

    border: 1px solid #ccc;

    border-radius: 8px;

    outline: none;

    font-size: 14px;
}}

#message-input:focus {{
    border-color: #111827;
}}

#send-button {{
    margin-left: 8px;

    height: 38px;

    padding: 0 14px;

    border: none;

    border-radius: 8px;

    background: #111827;

    color: white;

    cursor: pointer;

    font-size: 14px;
}}

#send-button:hover {{
    background: #374151;
}}

#send-button:disabled {{
    opacity: 0.5;

    cursor: not-allowed;
}}

.typing-message {{
    width: 55px;

    padding: 10px 12px;

    display: flex;

    align-items: center;
    justify-content: center;
}}

.typing {{
    display: flex;

    align-items: center;
    justify-content: center;

    gap: 4px;

    height: 14px;
}}

.typing span {{
    width: 6px;
    height: 6px;

    background: #777;

    border-radius: 50%;

    display: inline-block;

    animation: typing 1.4s infinite ease-in-out;
}}

.typing span:nth-child(1) {{
    animation-delay: 0s;
}}

.typing span:nth-child(2) {{
    animation-delay: 0.2s;
}}

.typing span:nth-child(3) {{
    animation-delay: 0.4s;
}}

@keyframes typing {{

    0%, 60%, 100% {{
        transform: translateY(0);
        opacity: 0.4;
    }}

    30% {{
        transform: translateY(-4px);
        opacity: 1;
    }}

}}

#chat-box::-webkit-scrollbar {{
    width: 5px;
}}

#chat-box::-webkit-scrollbar-track {{
    background: transparent;
}}

#chat-box::-webkit-scrollbar-thumb {{
    background: #ccc;

    border-radius: 10px;
}}

@media (max-width: 500px) {{

    .chat-container {{
        right: 10px;
        bottom: 85px;

        width: calc(100% - 20px);
        height: calc(100% - 100px);
    }}

    #chatbot-toggle {{
        right: 15px;
        bottom: 15px;
    }}

}}

</style>
</head>

<body>

<button id="chatbot-toggle">
    🤖
</button>

<div class="chat-container" id="chatbot">

    <h1>CopyHart AI Assistant</h1>

    <p>How can I help you?</p>

    <div id="chat-box">

    <div class="message bot">
    Hello! 👋 I'm CopyHart AI Assistant. 
    How can I help you today?
    </div>

    </div>

    <div class="input-area">

        <input
            type="text"
            id="message-input"
            placeholder="Type your message..."
            autocomplete="off"
        >

        <button id="send-button">
            Send
        </button>

    </div>

</div>


<script>

const BACKEND_URL = "{BACKEND_URL}";

const toggleButton =
    document.getElementById("chatbot-toggle");

const chatbot =
    document.getElementById("chatbot");

const input =
    document.getElementById("message-input");

const sendButton =
    document.getElementById("send-button");

const chatBox =
    document.getElementById("chat-box");


/* --------------------------------
   Open / Close Chatbot
-------------------------------- */

toggleButton.addEventListener("click", function() {{

    if (chatbot.style.display === "flex") {{

        chatbot.style.display = "none";

    }} else {{

        chatbot.style.display = "flex";

        input.focus();

    }}

}});


/* --------------------------------
   Add Message
-------------------------------- */

function addMessage(message, type) {{

    const div = document.createElement("div");

    div.className = "message " + type;

    div.textContent = message;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;

}}


/* --------------------------------
   Typing Indicator
-------------------------------- */

function showTyping() {{

    const div = document.createElement("div");

    div.className =
        "message bot typing-message";

    div.id = "typing-indicator";

    div.innerHTML = `
        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBox.appendChild(div);

    chatBox.scrollTop =
        chatBox.scrollHeight;

}}


function removeTyping() {{

    const typing =
        document.getElementById(
            "typing-indicator"
        );

    if (typing) {{
        typing.remove();
    }}

}}


/* --------------------------------
   Send Message
-------------------------------- */

async function sendMessage() {{

    const message =
        input.value.trim();

    if (!message) {{
        return;
    }}

    addMessage(
        message,
        "user"
    );

    input.value = "";

    sendButton.disabled = true;

    showTyping();


    try {{

        const response = await fetch(
            BACKEND_URL + "/chat",
            {{
                method: "POST",

                headers: {{
                    "Content-Type":
                        "application/json"
                }},

                body: JSON.stringify({{
                    question: message
                }})
            }}
        );


        if (!response.ok) {{

            throw new Error(
                "HTTP Error: " +
                response.status
            );

        }}


        const data =
            await response.json();


        removeTyping();


        const reply =
            data.answer ||
            data.response ||
            data.message ||
            data.reply ||
            "Sorry, I could not understand the response.";


        addMessage(
            reply,
            "bot"
        );


    }} catch (error) {{

        removeTyping();

        console.error(
            "Chatbot Error:",
            error
        );

        addMessage(
            "Sorry, I'm unable to connect to the server right now.",
            "bot"
        );

    }}


    sendButton.disabled = false;

    input.focus();

}}


/* --------------------------------
   Send Button
-------------------------------- */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* --------------------------------
   Enter Key
-------------------------------- */

input.addEventListener(
    "keydown",
    function(event) {{

        if (event.key === "Enter") {{

            event.preventDefault();

            sendMessage();

        }}

    }}
);

</script>

</body>
</html>
"""


components.html(
    html_code,
    height=900,
    scrolling=False
)
