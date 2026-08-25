from sentence_transformers import SentenceTransformer
from rag.vector_store import index
from rag.pdf_reader import chunks
import numpy as np


print("Loading local embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(question, top_k=5):

    question_vector = model.encode(
        [question],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        np.array(question_vector).astype("float32"),
        top_k
    )

    results = []

    for distance, i in zip(distances[0], indices[0]):

        results.append({
            "score": float(distance),
            "text": chunks[i]
        })

    return results


if __name__ == "__main__":

    question = input("\nEnter your question: ")

    results = retrieve(question)

    print("\n===== RETRIEVED RESULTS =====")

    for result in results:

        print("\n--- RESULT ---")
        print("Score:", result["score"])
        print(result["text"])