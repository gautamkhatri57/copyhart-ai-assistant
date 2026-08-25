import faiss
import numpy as np
from rag.embeddings import embeddings

vectors = np.array(embeddings).astype("float32")
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)

print("Total Vectors in FAISS: ", index.ntotal)
