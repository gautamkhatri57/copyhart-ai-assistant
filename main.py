from rag.retriever import retrieve
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


print("\n===== COPYHART AI ASSISTANT =====")
print("Type 'exit' to stop.\n")


while True:

    question = input("\nYou: ").strip()

    if question.lower() == "exit":
        break

    if not question:
        print("Please enter a question.")
        continue

    # Retrieve relevant information from FAISS
    results = retrieve(question, top_k=3)

    # Create context from retrieved chunks
    context = "\n\n".join(
        result["text"]
        for result in results
    )

    prompt = f"""
You are CopyHart AI Assistant.

Answer the user's question using ONLY the information provided
in the context below.

If the answer is not available in the context, say:
"I don't have enough information in the CopyHart service data to answer that."

Keep the answer clear, simple and professional.

Context:
{context}

User Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    print("\n===== COPYHART AI ASSISTANT =====")
    print(response.text)