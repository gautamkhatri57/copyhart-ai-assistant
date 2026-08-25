import os
import re
import json

from dotenv import load_dotenv
from google import genai

from rag.reranker import rerank


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(
    api_key=api_key
)


# =========================================================
# CONVERSATION STATE
# =========================================================

conversation_history = []

selected_service = None


# =========================================================
# UTILITY
# =========================================================

def clean_text(text):

    return re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text.lower()
    ).strip()


def get_history():

    return "\n".join(
        f"{item['role']}: {item['content']}"
        for item in conversation_history[-8:]
    )


# =========================================================
# AI INTENT ANALYSIS
# =========================================================

def analyze_intent(question):

    history = get_history()

    prompt = f"""
You are the intent analyzer for CopyHart AI Assistant.

Your job is to understand what the user wants.

Use the conversation history to understand context.

The user may mention:

- a broad service
- a specific service
- an activity
- a follow-up question
- a document question
- a process question
- a timeline question
- a requirement question

IMPORTANT:

If the user only mentions a broad service such as:

"trademark"
"copyright"
"patent"
"FSSAI"
"ISO"

and has NOT specified what they want to do with that service,
then clarification is required.

Example:

User: trademark

Return:

{{
    "needs_clarification": true,
    "service": "Trademark",
    "intent": "service_selection",
    "clarification": "Which trademark service are you looking for?"
}}

But:

User: trademark registration

Return:

{{
    "needs_clarification": false,
    "service": "Trademark Registration",
    "intent": "information_request",
    "clarification": ""
}}

And:

User: what documents are required?

If previous conversation is:

User: trademark registration

then understand that the user is asking:

"What documents are required for Trademark Registration?"

Return:

{{
    "needs_clarification": false,
    "service": "Trademark Registration",
    "intent": "documents",
    "clarification": ""
}}

Do NOT invent information.

Return ONLY valid JSON.

Conversation History:
{history}

Current User:
{question}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "temperature": 0.1
            }
        )

        text = response.text.strip()

        text = re.sub(
            r"```json|```",
            "",
            text
        ).strip()

        return json.loads(text)

    except Exception as e:

        print(f"Intent analysis error: {e}")

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

Retrieve information specifically relevant to this service
and this user question.
"""

    try:

        results = rerank(
            retrieval_query,
            top_k=5
        )

    except Exception as e:

        print(f"Reranker error: {e}")

        return ""

    context = "\n\n".join(
        result.get("text", "")
        for result in results
        if result.get("text")
    )

    return context


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

4. Use the conversation history to understand
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
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "temperature": 0.1
            }
        )

        return response.text.strip()

    except Exception as e:

        print(f"Gemini error: {e}")

        return (
            "Sorry, something went wrong while processing "
            "your request. Please try again."
        )


# =========================================================
# MAIN CHAT FUNCTION
# =========================================================

def chat(question):

    global selected_service

    question = question.strip()

    if not question:

        return "Please enter a question."

    # -----------------------------------------------------
    # Save User Message
    # -----------------------------------------------------

    conversation_history.append({
        "role": "user",
        "content": question
    })

    # -----------------------------------------------------
    # AI Intent Analysis
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
    # Update Current Service
    # -----------------------------------------------------

    if detected_service:

        selected_service = detected_service

    # -----------------------------------------------------
    # Clarification Required
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # RAG Retrieval
    # -----------------------------------------------------

    context = retrieve_information(
        question,
        selected_service
    )

    # -----------------------------------------------------
    # No Information
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Generate Final Answer
    # -----------------------------------------------------

    answer = generate_answer(
        question,
        selected_service,
        context
    )

    # -----------------------------------------------------
    # Save Assistant Response
    # -----------------------------------------------------

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    return answer