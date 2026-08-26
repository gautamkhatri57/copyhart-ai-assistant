import sys
import os

# =========================================================
# PROJECT ROOT PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORTS
# =========================================================

import streamlit as st

from chatbot import chat


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CopyHart AI Assistant",
    page_icon="🤖",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN APP
       Automatically follows Streamlit Light/Dark theme
       ===================================================== */

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }


    /* =====================================================
       MAIN CONTENT
       ===================================================== */

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }


    /* =====================================================
       HEADER
       ===================================================== */

    .header {
        background-color: var(--secondary-background-color);
        color: var(--text-color);

        padding: 22px;
        border-radius: 14px;

        text-align: center;

        margin-bottom: 20px;

        border: 1px solid rgba(128, 128, 128, 0.20);
    }

    .header h1 {
        margin: 0;
        font-size: 25px;
        font-weight: 700;
        color: var(--text-color);
    }

    .header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        color: var(--text-color);
        opacity: 0.7;
    }


    /* =====================================================
       CHAT MESSAGE
       ===================================================== */

    [data-testid="stChatMessage"] {
        color: var(--text-color);
    }

    [data-testid="stChatMessage"] p {
        color: var(--text-color);
    }


    /* =====================================================
       CHAT INPUT
       ===================================================== */

    [data-testid="stChatInput"] {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
    }

    [data-testid="stChatInput"] textarea {
        color: var(--text-color);
    }


    /* =====================================================
       CHAT INPUT PLACEHOLDER
       ===================================================== */

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-color);
        opacity: 0.55;
    }


    /* =====================================================
       REMOVE EXTRA BUTTONS
       ===================================================== */

    .stButton {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="header">
        <h1>🤖 CopyHart AI Assistant</h1>
        <p>How can I help you?</p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm CopyHart AI Assistant. "
                "How can I help you today?"
            )
        }
    ]


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    avatar = (
        "🤖"
        if message["role"] == "assistant"
        else "👤"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.write(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Type your message..."
)


# =========================================================
# PROCESS MESSAGE
# =========================================================

if question:

    question = question.strip()

    if not question:
        st.stop()


    # =====================================================
    # USER MESSAGE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.write(question)


    # =====================================================
    # AI RESPONSE
    # =====================================================

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner("Thinking..."):

            try:

                answer = chat(question)

            except Exception as e:

                print(
                    f"Chat error: {e}"
                )

                answer = (
                    "Sorry, something went wrong "
                    "while processing your request."
                )

        st.write(answer)


    # =====================================================
    # SAVE RESPONSE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )