
from sentence_transformers import SentenceTransformer
from rag.pdf_reader import chunks
import numpy as np
import os

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute path to embeddings file
DATA_DIR = os.path.join(BASE_DIR, "data")
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.npy")

# Make sure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

print("Loading local embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


if os.path.exists(EMBEDDINGS_FILE):

    print("Loading saved embeddings...")

    embeddings = np.load(
        EMBEDDINGS_FILE,
        allow_pickle=True
    )

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

