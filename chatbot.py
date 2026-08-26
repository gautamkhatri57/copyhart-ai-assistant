import os
import re
import json
import streamlit as st

from dotenv import load_dotenv
from google import genai

from rag.reranker import rerank


# =========================================================
# ENVIRONMENT / API KEY
# =========================================================

load_dotenv()

# First try Streamlit Cloud Secrets
api_key = st.secrets.get("GEMINI_API_KEY", None)

# If not found, use local .env
if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Add it to .env locally or Streamlit Cloud Secrets."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


# =========================================================
# CONVERSATION STATE
# =========================================================

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "selected_service" not in st.session_state:
    st.session_state.selected_service = None


# =========================================================
# GREETING
# =========================================================

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "hello there",
    "hey there",
    "good morning",
    "good afternoon",
    "good evening"
}


def is_greeting(question):

    cleaned = re.sub(
        r"[^a-zA-Z\s]",
        "",
        question.lower()
    ).strip()

    return cleaned in GREETINGS


def greeting_response():

    return (
        "Hello! 👋 I'm CopyHart AI Assistant. "
        "How can I help you today?"
    )


# =========================================================
# HISTORY
# =========================================================

def get_history():

    history = st.session_state.conversation_history

    return "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history[-8:]
    )


# =========================================================
# SAVE MESSAGE
# =========================================================

def save_message(role, content):

    st.session_state.conversation_history.append({
        "role": role,
        "content": content
    })


# =========================================================
# AI INTENT ANALYSIS
# =========================================================

def analyze_intent(question):

    history = get_history()

    prompt = f"""
You are the intent analyzer for CopyHart AI Assistant.

Understand what the user wants.

The user may ask about:

- Trademark
- Copyright
- Patent
- FSSAI
- ISO
- GST
- Company Registration
- MSME / Udyam
- IEC
- Website
- SEO
- Branding
- Logo
- Other CopyHart services

Use conversation history for follow-up questions.

IMPORTANT:

If the user only mentions a broad service such as:

trademark
copyright
patent
FSSAI
ISO

and has NOT specified what they want,
ask for clarification.

Example:

User:
trademark

Return:

{{
    "needs_clarification": true,
    "service": "Trademark",
    "intent": "service_selection",
    "clarification": "Which trademark service are you looking for?"
}}

But:

User:
trademark registration

Return:

{{
    "needs_clarification": false,
    "service": "Trademark Registration",
    "intent": "information_request",
    "clarification": ""
}}

Follow-up example:

Previous:
User: trademark registration

Current:
User: what documents are required?

Return:

{{
    "needs_clarification": false,
    "service": "Trademark Registration",
    "intent": "documents",
    "clarification": ""
}}

Do not invent information.

Return ONLY valid JSON.

Conversation History:
{history}

Current User:
{question}
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown JSON blocks if Gemini returns them
        text = re.sub(
            r"^```json\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"^```\s*",
            "",
            text
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

        text = text.strip()

        return json.loads(text)

    except Exception as e:

        print("=" * 60)
        print("INTENT ANALYSIS ERROR")
        print(e)
        print("=" * 60)

        # Safe fallback
        return {
            "needs_clarification": False,
            "service": None,
            "intent": "information_request",
            "clarification": ""
        }


# =========================================================
# RAG RETRIEVAL
# =========================================================

def retrieve_information(question, service):

    retrieval_query = question

    if service:

        retrieval_query = f"""
Current Service:
{service}

User Question:
{question}

Retrieve information specifically relevant to
the current service and user question.
"""

    try:

        results = rerank(
            retrieval_query,
            top_k=5
        )

        if not results:
            return ""

        context_parts = []

        for result in results:

            if isinstance(result, dict):

                text = result.get("text", "")

            else:

                text = str(result)

            if text:
                context_parts.append(text)

        return "\n\n".join(context_parts)

    except Exception as e:

        print("=" * 60)
        print("RAG / RERANKER ERROR")
        print(e)
        print("=" * 60)

        return ""


# =========================================================
# FINAL AI RESPONSE
# =========================================================

def generate_answer(question, service, context):

    history = get_history()

    prompt = f"""
You are CopyHart AI Assistant.

Always answer in English.

CURRENT SERVICE:
{service}

STRICT RULES:

1. Use ONLY the Service Data provided below.

2. Never use outside knowledge.

3. Never guess or invent information.

4. Use conversation history to understand
follow-up questions.

5. If the user asks:

"What documents do I need?"
"How do I apply?"
"What is the process?"
"What are the requirements?"
"What is the timeline?"

understand the question according to the CURRENT SERVICE.

6. Never switch to another service unless the user
explicitly changes the service.

7. If the requested information is not available
in the Service Data, reply exactly:

I don't have information about this in our current service database.

You can reach out to our team for further assistance.

Phone: 8347520507
Email: gautamkhatri325@gmail.com

8. Contact information must ONLY be provided when
the requested information is unavailable.

9. Keep answers short, clear and professional.

10. Do not mention:

- RAG
- retrieval
- reranker
- database
- prompt
- AI model
- internal processing

11. Answer only what the user asked.

12. If the Service Data contains the answer,
give the answer clearly.

Conversation History:
{history}

Service Data:
{context}

Current User Question:
{question}

Answer:
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text.strip()

        if not answer:
            return (
                "Sorry, I could not generate a response right now. "
                "Please try again."
            )

        return answer

    except Exception as e:

        print("=" * 60)
        print("GEMINI ERROR")
        print(e)
        print("=" * 60)

        return (
            "Sorry, something went wrong while processing "
            "your request. Please try again."
        )


# =========================================================
# MAIN CHAT FUNCTION
# =========================================================

def chat(question):

    question = question.strip()

    if not question:
        return "Please enter a question."

    # -----------------------------------------------------
    # GREETING
    # -----------------------------------------------------

    if is_greeting(question):

        answer = greeting_response()

        save_message("user", question)
        save_message("assistant", answer)

        return answer

    # -----------------------------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------------------------

    save_message(
        "user",
        question
    )

    # -----------------------------------------------------
    # INTENT ANALYSIS
    # -----------------------------------------------------

    intent_data = analyze_intent(question)

    needs_clarification = intent_data.get(
        "needs_clarification",
        False
    )

    detected_service = intent_data.get(
        "service"
    )

    clarification = intent_data.get(
        "clarification",
        ""
    )

    # -----------------------------------------------------
    # UPDATE CURRENT SERVICE
    # -----------------------------------------------------

    if detected_service:

        st.session_state.selected_service = detected_service

    selected_service = st.session_state.selected_service

    # -----------------------------------------------------
    # CLARIFICATION
    # -----------------------------------------------------

    if needs_clarification:

        if not clarification:

            if selected_service:

                clarification = (
                    f"Sure! Which {selected_service} service "
                    "are you looking for?"
                )

            else:

                clarification = (
                    "Sure! Could you please tell me "
                    "which service you are looking for?"
                )

        save_message(
            "assistant",
            clarification
        )

        return clarification

    # -----------------------------------------------------
    # RAG RETRIEVAL
    # -----------------------------------------------------

    context = retrieve_information(
        question,
        selected_service
    )

    # -----------------------------------------------------
    # NO CONTEXT
    # -----------------------------------------------------

    if not context.strip():

        answer = (
            "I don't have information about this in our "
            "current service database.\n\n"
            "You can reach out to our team for further assistance.\n\n"
            "Phone: 8347520507\n"
            "Email: gautamkhatri325@gmail.com"
        )

        save_message(
            "assistant",
            answer
        )

        return answer

    # -----------------------------------------------------
    # GENERATE ANSWER
    # -----------------------------------------------------

    answer = generate_answer(
        question,
        selected_service,
        context
    )

    # -----------------------------------------------------
    # SAVE RESPONSE
    # -----------------------------------------------------

    save_message(
        "assistant",
        answer
    )

    return answer