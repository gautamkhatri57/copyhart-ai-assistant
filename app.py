import time
import re

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rag.retriever import retrieve
from rag.reranker import rerank

import ollama


app = FastAPI()

conversation_history = []
selected_service = None


class ChatRequest(BaseModel):
    question: str


app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


@app.get("/")
def home():
    return FileResponse("frontend/index.html")


def clean_text(text):
    return re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text.lower()
    ).strip()


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
        "branding"
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


def detect_service(question):
    q = clean_text(question)

    service_keywords = {
        "trademark": [
            "trademark",
            "trade mark"
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
            "bis certification",
            "bis"
        ],
        "spice": [
            "spice board",
            "spice certification"
        ],
        "iso 9001": [
            "iso 9001"
        ],
        "iso 13485": [
            "iso 13485"
        ],
        "iso 14001": [
            "iso 14001"
        ],
        "iso 22000": [
            "iso 22000"
        ],
        "iso 45001": [
            "iso 45001"
        ],
        "iso 27001": [
            "iso 27001"
        ],
        "gmp": [
            "gmp",
            "good manufacturing"
        ],
        "logo": [
            "logo design",
            "logo making",
            "logo"
        ],
        "website": [
            "website development",
            "custom website",
            "website",
            "seo"
        ],
        "brand": [
            "branding",
            "brand development",
            "brand marketing"
        ]
    }

    fallback = {
        "trademark": "Trademark Registration",
        "copyright": "Copyright Registration",
        "patent": "Patent Registration",
        "fssai": "FSSAI License & Registration",
        "msme": "MSME / Udyam Registration",
        "iec": "IEC Registration",
        "apeda": "APEDA Registration / RCMC",
        "barcode": "Barcode Registration",
        "bis": "BIS Certification",
        "spice": "Spice Board Certification",
        "iso 9001": "ISO 9001 Certification",
        "iso 13485": "ISO 13485 Medical Devices",
        "iso 14001": "ISO 14001 Environmental Management",
        "iso 22000": "ISO 22000 Food Safety Management",
        "iso 45001": "ISO 45001 Occupational Health & Safety",
        "iso 27001": "ISO 27001 Information Security",
        "gmp": "Good Manufacturing Practices (GMP) Certification",
        "logo": "Logo Design and Making",
        "website": "Custom Websites & SEO",
        "brand": "Brand Development & Marketing"
    }

    for service, keywords in service_keywords.items():

        if any(keyword in q for keyword in keywords):

            results = retrieve(
                question,
                top_k=10
            )

            for result in results:

                text = result.get("text", "")

                if not text:
                    continue

                first_line = (
                    text.strip()
                    .splitlines()[0]
                    .strip()
                )

                if service in clean_text(first_line):
                    return first_line

            return fallback.get(service)

    return None


def is_service_only_question(question):
    q = clean_text(question)

    service_only_terms = [
        "trademark",
        "trade mark",
        "copyright",
        "patent",
        "fssai",
        "food license",
        "food licence",
        "msme",
        "udyam",
        "iec",
        "apeda",
        "barcode",
        "gtin",
        "gs1",
        "bis",
        "spice board",
        "iso 9001",
        "iso 13485",
        "iso 14001",
        "iso 22000",
        "iso 45001",
        "iso 27001",
        "gmp",
        "logo",
        "website",
        "seo",
        "branding"
    ]

    return q in service_only_terms


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


def is_generic_followup(question):
    q = clean_text(question)

    followups = [
        "what documents",
        "which documents",
        "documents required",
        "required documents",
        "how can i apply",
        "how do i apply",
        "how to apply",
        "what is the process",
        "process",
        "how long",
        "timeline",
        "eligibility",
        "what are the requirements",
        "requirements",
        "what is it",
        "tell me more",
        "how does it work"
    ]

    return any(
        phrase in q
        for phrase in followups
    )


@app.post("/chat")
def chat(request: ChatRequest):

    global selected_service

    total_start = time.time()

    question = request.question.strip()

    if not question:
        return {
            "answer": "Please enter a question."
        }

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

        return {
            "answer": answer
        }

    detected_service = detect_service(question)

    if detected_service:

        selected_service = detected_service

        if is_service_only_question(question):

            answer = (
                f"Sure. What would you like to know about "
                f"{detected_service}? "
                f"You can ask about the process, required "
                f"documents, eligibility, timeline, or other details."
            )

            conversation_history.append({
                "role": "user",
                "content": question
            })

            conversation_history.append({
                "role": "assistant",
                "content": answer
            })

            return {
                "answer": answer
            }

    elif not is_generic_followup(question):

        if not selected_service:

            answer = (
                "Could you please specify which CopyHart "
                "service you are referring to?"
            )

            conversation_history.append({
                "role": "user",
                "content": question
            })

            conversation_history.append({
                "role": "assistant",
                "content": answer
            })

            return {
                "answer": answer
            }

    retrieval_query = question

    if selected_service:

        retrieval_query = f"""
Service: {selected_service}

User Question: {question}

Find information specifically relevant to this user question
within this service.
"""

    retrieval_start = time.time()

    results = retrieve(
        retrieval_query,
        top_k=10
    )

    retrieval_time = time.time() - retrieval_start

    print(
        f"Retrieval time: {retrieval_time:.2f} seconds"
    )

    rerank_start = time.time()

    try:

        reranked_results = rerank(
            question=retrieval_query,
            documents=results,
            top_k=5
        )

    except TypeError:

        try:

            reranked_results = rerank(
                retrieval_query,
                top_k=5
            )

        except Exception as e:

            print(
                "Reranker error:",
                str(e)
            )

            reranked_results = results[:5]

    except Exception as e:

        print(
            "Reranker error:",
            str(e)
        )

        reranked_results = results[:5]

    rerank_time = time.time() - rerank_start

    print(
        f"Reranker time: {rerank_time:.2f} seconds"
    )

    context = "\n\n".join(
        result.get("text", "")
        for result in reranked_results
        if result.get("text")
    )

    history = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in conversation_history[-6:]
    )

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
"How long does it take?"
"What are the requirements?"

must be answered for the CURRENT SERVICE.

6. Do NOT switch to another service just because
another retrieved result looks similar.

7. If the user asks about a specific activity that
is NOT actually described in the Service Data,
do NOT substitute a similar service.

If the requested information is unavailable,
reply exactly:

I don't have information about this in our current service database.

You can reach out to our team for further assistance.

Phone: 8347520507
Email: gautamkhatri325@gmail.com

8. Contact information must ONLY be provided when
the requested information is unavailable.

9. Keep normal answers short, clear and professional.

10. Do not mention retrieval, context, database,
AI model, reranker or internal processing.

11. If the Service Data contains the answer,
answer directly and clearly.

12. Do not add information that is not present
in the Service Data.

Previous Conversation:
{history}

Service Data:
{context}

Current User Question:
{question}

Answer:
"""

    ollama_start = time.time()

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.1
        }
    )

    answer = response["message"]["content"].strip()

    ollama_time = time.time() - ollama_start

    print(
        f"Ollama time: {ollama_time:.2f} seconds"
    )

    conversation_history.append({
        "role": "user",
        "content": question
    })

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    total_time = time.time() - total_start

    print(
        f"Total response time: {total_time:.2f} seconds"
    )

    print("-" * 50)

    return {
        "answer": answer
    }