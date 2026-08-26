import os
import re
import time

from dotenv import load_dotenv
from google import genai

from rag.reranker import rerank


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# API KEY
# Supports:
# 1. Local .env
# 2. Streamlit Cloud Secrets
# =========================================================

def get_api_key():

    # Local .env
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    # Streamlit Cloud
    try:
        import streamlit as st

        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]

    except Exception:
        pass

    return None


# =========================================================
# GEMINI CLIENT
# =========================================================

api_key = get_api_key()

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Add GEMINI_API_KEY to Streamlit Cloud Secrets."
    )

client = genai.Client(
    api_key=api_key
)


# =========================================================
# MODEL
# =========================================================

MODEL_NAME = "gemini-3.6-flash"


# =========================================================
# CONVERSATION STATE
# =========================================================

conversation_history = []

selected_service = None


# =========================================================
# GREETING
# =========================================================

def is_greeting(question):

    q = question.lower().strip()

    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "hey there",
        "hello there"
    }

    return q in greetings


def greeting_response():

    return (
        "Hello! 👋 I'm CopyHart AI Assistant. "
        "How can I help you today?"
    )


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    return re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text.lower()
    ).strip()


# =========================================================
# GENERIC REQUEST
# =========================================================

def is_generic_request(question):

    q = clean_text(question)

    generic_terms = [
        "renewal",
        "renew",
        "registration",
        "register",
        "certification",
        "certificate"
    ]

    services = [
        "trademark",
        "trade mark",
        "copyright",
        "patent",
        "fssai",
        "food license",
        "food licence",
        "iso",
        "msme",
        "udyam",
        "iec",
        "apeda",
        "barcode",
        "bis",
        "spice",
        "logo",
        "website",
        "seo",
        "branding",
        "brand",
        "legal"
    ]

    has_generic = any(
        term in q
        for term in generic_terms
    )

    has_service = any(
        service in q
        for service in services
    )

    return has_generic and not has_service


# =========================================================
# DETECT SERVICE
# =========================================================

def detect_service(question):

    q = clean_text(question)

    service_keywords = {

        "trademark": [
            "trademark",
            "trade mark",
            "brand registration",
            "brand name registration"
        ],

        "copyright": [
            "copyright"
        ],

        "patent": [
            "patent"
        ],

        "fssai": [
            "fssai",
            "food license",
            "food licence",
            "food registration"
        ],

        "msme": [
            "msme",
            "udyam"
        ],

        "iec": [
            "iec",
            "import export code"
        ],

        "apeda": [
            "apeda"
        ],

        "barcode": [
            "barcode",
            "gtin",
            "gs1"
        ],

        "bis": [
            "bis certification"
        ],

        "spice": [
            "spice board",
            "spice certification"
        ],

        "iso9001": [
            "iso 9001"
        ],

        "iso13485": [
            "iso 13485"
        ],

        "iso14001": [
            "iso 14001"
        ],

        "iso22000": [
            "iso 22000"
        ],

        "iso45001": [
            "iso 45001"
        ],

        "iso27001": [
            "iso 27001"
        ],

        "gmp": [
            "gmp",
            "good manufacturing practices"
        ],

        "logo": [
            "logo design",
            "logo making"
        ],

        "website": [
            "website development",
            "custom website",
            "seo"
        ],

        "brand": [
            "branding",
            "brand development",
            "brand marketing"
        ],

        # =================================================
        # LEGAL SERVICES
        # =================================================

        "legal": [
            "legal services",
            "legal service",
            "legal sevices",
            "legal help",
            "legal support",
            "legal assistance"
        ]
    }


    service_names = {

        "trademark":
            "Trademark Registration",

        "copyright":
            "Copyright Registration",

        "patent":
            "Patent Registration / Filing",

        "fssai":
            "FSSAI License & Registration",

        "msme":
            "MSME / Udyam Registration",

        "iec":
            "IEC Registration",

        "apeda":
            "APEDA Registration / RCMC",

        "barcode":
            "Barcode Registration",

        "bis":
            "BIS Certification",

        "spice":
            "Spice Board Registration",

        "iso9001":
            "ISO 9001 Certification",

        "iso13485":
            "ISO 13485 Medical Devices",

        "iso14001":
            "ISO 14001 Environmental Management",

        "iso22000":
            "ISO 22000 Food Safety Management",

        "iso45001":
            "ISO 45001 Occupational Health & Safety",

        "iso27001":
            "ISO 27001 Information Security",

        "gmp":
            "Good Manufacturing Practices (GMP) Certification",

        "logo":
            "Logo Design and Making",

        "website":
            "Custom Websites & SEO",

        "brand":
            "Brand Development & Marketing",

        "legal":
            "Legal Services"
    }


    for service, keywords in service_keywords.items():

        for keyword in keywords:

            if keyword in q:

                return service_names.get(service)


    return None


# =========================================================
# GENERIC FOLLOW-UP
# =========================================================

def is_generic_followup(question):

    q = clean_text(question)

    followups = [

        # -------------------------------------------------
        # DEFINITION / GENERAL
        # -------------------------------------------------

        "what is",
        "what are",
        "what does",
        "what do",
        "what is it",
        "what is this",
        "what does it mean",

        "tell me about",
        "tell me more",
        "explain",
        "explain it",
        "explain this",

        # -------------------------------------------------
        # DOCUMENTS
        # -------------------------------------------------

        "what documents",
        "which documents",
        "documents required",
        "required documents",
        "documents needed",
        "what documents do i need",
        "which documents do i need",

        # -------------------------------------------------
        # APPLICATION
        # -------------------------------------------------

        "how can i apply",
        "how do i apply",
        "how to apply",

        "how can i register",
        "how do i register",
        "how to register",

        # -------------------------------------------------
        # PROCESS
        # -------------------------------------------------

        "what is the process",
        "what's the process",
        "process",
        "how does it work",
        "how it works",

        # -------------------------------------------------
        # REQUIREMENTS
        # -------------------------------------------------

        "what are the requirements",
        "requirements",

        "eligibility",
        "who is eligible",

        # -------------------------------------------------
        # TIMELINE
        # -------------------------------------------------

        "how long",
        "timeline",
        "how much time",
        "how many days"
    ]


    return any(
        phrase in q
        for phrase in followups
    )


# =========================================================
# CLARIFICATION
# =========================================================

def clarification_message(question):

    q = clean_text(question)

    if "renewal" in q or "renew" in q:

        return (
            "Sure. Which renewal service are you looking for? "
            "Please specify the service, such as Trademark, "
            "Copyright, FSSAI, ISO, or another service."
        )

    if "registration" in q or "register" in q:

        return (
            "Sure. Which registration service are you looking for? "
            "Please specify the service, such as Trademark, "
            "Copyright, FSSAI, MSME, IEC, or another service."
        )

    if "certification" in q or "certificate" in q:

        return (
            "Sure. Which certification service are you looking for? "
            "Please specify the service, such as ISO, BIS, FSSAI, "
            "or another certification."
        )

    return (
        "Sure. Could you please specify which CopyHart service "
        "you are looking for?"
    )


# =========================================================
# LEGAL SERVICES RESPONSE
# =========================================================

def legal_services_response():

    return """
CopyHart provides support for various legal and
intellectual-property services, including:

• Trademark Registration
• Trademark Objection / Examination Reply
• Trademark Hearing
• Trademark Renewal
• Trademark Opposition
• Trademark Rectification
• Trademark Assignment / Ownership Transfer
• Trademark Licensing
• International Trademark Registration (Madrid)
• Well-Known Trademark Services
• Copyright Registration
• Patent Registration / Filing
• Patent Prior-Art Search
• Provisional Patent Filing
• PCT Filing
• Design Registration
• Geographical Indication (GI) Tag
• IP Monitoring & Journaling
• IP Portfolio Audit

If you tell me your specific requirement, I can help identify
the most relevant CopyHart service.
""".strip()


# =========================================================
# UNAVAILABLE ANSWER
# =========================================================

def unavailable_answer():

    return (
        "I don't have information about this in our current "
        "service database.\n\n"
        "You can reach out to our team for further assistance.\n\n"
        "Phone: 8347520507\n"
        "Email: gautamkhatri325@gmail.com"
    )


# =========================================================
# MAIN CHAT FUNCTION
# =========================================================

def chat(question):

    global selected_service

    total_start = time.time()

    question = question.strip()

    if not question:

        return "Please enter a question."


    # =====================================================
    # GREETING
    # =====================================================

    if is_greeting(question):

        answer = greeting_response()

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
    # LEGAL SERVICES
    # =====================================================

    clean_question = clean_text(question)

    legal_queries = [
        "legal",
        "legal service",
        "legal services",
        "legal sevices",
        "legal help",
        "legal support",
        "legal assistance"
    ]

    if clean_question in legal_queries:

        selected_service = "Legal Services"

        answer = legal_services_response()

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
    # GENERIC REQUEST
    # =====================================================

    if is_generic_request(question):

        answer = clarification_message(question)

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
    # DETECT SERVICE
    # =====================================================

    detected_service = detect_service(question)

    if detected_service:

        selected_service = detected_service


    # =====================================================
    # FOLLOW-UP
    # =====================================================

    elif is_generic_followup(question):

        if selected_service:

            pass

        else:

            selected_service = None


    # =====================================================
    # RETRIEVAL QUERY
    # =====================================================

    retrieval_query = question

    if selected_service:

        retrieval_query = f"""
Service: {selected_service}

User Question: {question}

Find information specifically relevant to this user question
within this service.
"""


    # =====================================================
    # RERANK / RETRIEVAL
    # =====================================================

    retrieval_start = time.time()

    try:

        results = rerank(
            retrieval_query,
            top_k=5
        )

    except Exception as e:

        print(
            f"RERANKER ERROR: {type(e).__name__}: {e}"
        )

        return (
            "Sorry, I am unable to access the service "
            "information right now. Please try again."
        )


    retrieval_time = time.time() - retrieval_start

    print(
        f"Retrieval time: {retrieval_time:.2f} seconds"
    )


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context = "\n\n".join(

        result.get("text", "")

        for result in results

        if isinstance(result, dict)
        and result.get("text")
    )


    # =====================================================
    # NO CONTEXT
    # =====================================================

    if not context.strip():

        answer = unavailable_answer()

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
    # CONVERSATION HISTORY
    # =====================================================

    history = "\n".join(

        f"{item['role']}: {item['content']}"

        for item in conversation_history[-6:]
    )


    # =====================================================
    # GEMINI PROMPT
    # =====================================================

    prompt = f"""
You are CopyHart AI Assistant.

Always answer in English.

CURRENT SERVICE:
{selected_service}

STRICT RULES:

1. Use ONLY the Service Data provided below.

2. Never use outside knowledge.

3. Never guess or invent information.

4. The CURRENT SERVICE has priority for generic
follow-up questions.

5. Generic follow-up questions such as:

"What documents do I need?"
"How do I apply?"
"What is the process?"
"What are the requirements?"
"What is it?"
"Tell me about it."
"Explain it."

must be answered for the CURRENT SERVICE.

6. Do NOT switch to another service because another
retrieved result looks similar.

7. If the user asks about a specific activity, process,
requirement, document, timeline or other information that
is NOT actually described in the Service Data, do NOT
use a similar service as a substitute.

8. If the requested information is unavailable in the
Service Data, reply exactly:

I don't have information about this in our current service database.

You can reach out to our team for further assistance.

Phone: 8347520507
Email: gautamkhatri325@gmail.com

9. Contact information must ONLY be provided when the
requested information is unavailable.

10. Keep normal answers short, clear and professional.

11. Do not mention context, retrieval, database, RAG,
reranker, AI model, prompt or internal processing.

12. Do not make assumptions based on general knowledge.

13. Answer only what the user asked.

14. If the Service Data contains the exact answer,
give that answer clearly.

Previous Conversation:
{history}

Service Data:
{context}

Current User Question:
{question}

Answer:
"""


    # =====================================================
    # GEMINI
    # =====================================================

    gemini_start = time.time()

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config={
                "temperature": 0.1
            }
        )

        answer = response.text.strip()


    except Exception as e:

        print(
            f"GEMINI ERROR: {type(e).__name__}: {e}"
        )

        return (
            "Sorry, something went wrong while processing "
            "your request. Please try again."
        )


    gemini_time = time.time() - gemini_start

    print(
        f"Gemini time: {gemini_time:.2f} seconds"
    )


    # =====================================================
    # SAVE HISTORY
    # =====================================================

    conversation_history.append({
        "role": "user",
        "content": question
    })

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })


    # =====================================================
    # TOTAL TIME
    # =====================================================

    total_time = time.time() - total_start

    print(
        f"Total response time: {total_time:.2f} seconds"
    )

    print("-" * 50)


    return answer