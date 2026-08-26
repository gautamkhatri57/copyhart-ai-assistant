from sentence_transformers import SentenceTransformer
from rag.vector_store import index
from rag.pdf_reader import chunks

import numpy as np


# =========================================================
# LOAD MODEL ONCE
# =========================================================

print("Loading local embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# =========================================================
# RETRIEVE
# =========================================================

def retrieve(question, top_k=5):

    question_vector = model.encode(
        [question],
        convert_to_numpy=True
    )

    question_vector = np.asarray(
        question_vector,
        dtype="float32"
    )

    distances, indices = index.search(
        question_vector,
        top_k
    )

    results = []

    for distance, i in zip(
        distances[0],
        indices[0]
    ):

        if i < 0 or i >= len(chunks):
            continue

        results.append({
            "score": float(distance),
            "text": chunks[i]
        })

    return results


# =========================================================
# RERANK
# =========================================================

def rerank(question, top_k=5):

    results = retrieve(
        question,
        top_k=top_k
    )

    return results