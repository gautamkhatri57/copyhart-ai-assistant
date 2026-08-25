from sentence_transformers import SentenceTransformer
from rag.pdf_reader import chunks
import numpy as np
import os

EMBEDDINGS_FILE = "data/embeddings.npy"

print("Loading local embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


if os.path.exists(EMBEDDINGS_FILE):

    print("Loading saved embeddings...")

    embeddings = np.load(
        EMBEDDINGS_FILE,
        allow_pickle=True
    ).tolist()

else:

    print("Creating local embeddings...")

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    np.save(
        EMBEDDINGS_FILE,
        embeddings
    )

    print("Embeddings saved.")


print("Embedding dimension:", len(embeddings[0]))