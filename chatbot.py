import os
import re
import json
import streamlit as st

from dotenv import load_dotenv
from google import genai

from rag.reranker import rerank


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

# Local .env
api_key = os.getenv("GEMINI_API_KEY")

# Streamlit Cloud Secrets
try:
    if not api_key:
        api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Add it to .env or Streamlit Secrets."
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


# =========================================================
# CONVERSATION
# =========================================================

conversation_history = []
selected_service = None


# =========================================================
# GREETING
# =========================================================

def is_greeting(text):

    text = text.lower().strip()

    greetings = [
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "hey there",
        "hello there"
    ]

    return text in greetings


# =========================================================
# UTILITY
# =========================================================

def get_history():

    if not conversation_history:
        return ""

    return "\n".join(
        f"{item['role']}: {item['content']}"
        for item in conversation_history[-8:]
    )


# =========================================================
# INTENT ANALYSIS
# =========================================================

def analyze_intent(question):

    history = get_history()

    prompt = f"""
You are the intent analyzer for CopyHart AI Assistant.

Understand the user's request.

If the user only mentions a broad service such as:

trademark
copyright
patent
FSSAI
ISO

and does not specify what they want,
ask a clarification question.

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

Example:

User:
trademark registration

Return:

{{
    "needs_clarification": false,
    "service": "Trademark Registration",
    "intent": "information_request",
    "clarification": ""
}}

If the previous service was FSSAI and the user says:

what documents are required?

understand that they mean:

documents required for FSSAI.

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

        # Remove markdown JSON fences
        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)
        text = text.strip()

        return json.loads(text)

    except Exception as e:

        print("INTENT ERROR:", repr(e))

        # Do not stop the chatbot if intent analysis fails
        return {
            "needs_clarification": False,
            "service": None,
            "intent": "information_request",
            "clarification": ""
        }


# =========================================================
# RAG RETRIEVAL
# =========================================================

def retrieve_information(question, service=None):

    if service:

        retrieval_query = f"""
Service: {service}

User Question:
{question}
"""

    else:

        retrieval_query = question

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

            if text and text.strip():

                context_parts.append(text.strip())

        return "\n\n".join(context_parts)

    except Exception as e:

        print("RAG ERROR:", repr(e))

        return ""


# =========================================================
# FINAL ANSWER
# =========================================================

def generate_answer(question, service, context):

    history = get_history()

    prompt = f"""
You are CopyHart AI Assistant.

Answer the user using ONLY the Service Data below.

RULES:

1. Always answer in English.

2. Do NOT use outside knowledge.

3. Do NOT invent information.

4. Use conversation history for follow-up questions.

5. If the user asks:
   - documents
   - process
   - requirements
   - timeline
   - eligibility
   - procedure

   understand the question according to the current service.

6. Do not switch services unless the user explicitly changes
the service.

7. If the Service Data contains the answer,
answer clearly and directly.

8. If the Service Data does NOT contain the requested information,
reply exactly:

I don't have information about this in our current service database.

You can reach out to our team for further assistance.

Phone: 8347520507
Email: gautamkhatri325@gmail.com

9. Do not provide contact information when the answer exists
in the Service Data.

10. Keep answers short, clear and professional.

11. Never mention:
- RAG
- reranker
- database
- embeddings
- vector
- prompt
- AI model
- internal processing

12. Answer only what the user asked.

Current Service:
{service}

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

        answer = response.text

        if not answer:
            return (
                "I don't have information about this in our "
                "current service database."
            )

        return answer.strip()

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        return (
            "Sorry, something went wrong while processing "
            "your request. Please try again."
        )


# =========================================================
# MAIN CHAT
# =========================================================

def chat(question):

    global selected_service

    question = question.strip()

    if not question:

        return "Please enter a question."

    # =====================================================
    # GREETING
    # =====================================================

    if is_greeting(question):

        answer = (
            "Hello! 👋 I'm CopyHart AI Assistant. "
            "How can I help you today?"
        )

        conversation_history.append({
            "role": "user",
            "content": question
        })

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    # =====================================================
    # SAVE USER MESSAGE
    # =====================================================

    conversation_history.append({
        "role": "user",
        "content": question
    })

    # =====================================================
    # INTENT
    # =====================================================

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

    # =====================================================
    # SERVICE
    # =====================================================

    if detected_service:

        selected_service = detected_service

    # =====================================================
    # CLARIFICATION
    # =====================================================

    if needs_clarification:

        if not clarification:

            clarification = (
                f"Sure! Which {selected_service} service "
                "are you looking for?"
            )

        conversation_history.append({
            "role": "assistant",
            "content": clarification
        })

        return clarification

    # =====================================================
    # RAG
    # =====================================================

    context = retrieve_information(
        question,
        selected_service
    )

    # =====================================================
    # NO CONTEXT
    # =====================================================

    if not context.strip():

        answer = (
            "I don't have information about this in our "
            "current service database.\n\n"
            "You can reach out to our team for further assistance.\n\n"
            "Phone: 8347520507\n"
            "Email: gautamkhatri325@gmail.com"
        )

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    # =====================================================
    # GEMINI
    # =====================================================

    answer = generate_answer(
        question,
        selected_service,
        context
    )

    # =====================================================
    # SAVE ANSWER
    # =====================================================

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    return answer