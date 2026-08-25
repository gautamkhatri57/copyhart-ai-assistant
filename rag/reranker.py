from rag.retriever import retrieve


def rerank(question, top_k=5):
    """
    Lightweight reranking for deployment.

    Uses FAISS retrieval results directly instead of loading
    a separate CrossEncoder model.
    """

    results = retrieve(question, top_k=top_k)

    if not results:
        return []

    return [
        {
            "score": result.get("score", 0.0),
            "text": result.get("text", "")
        }
        for result in results
        if result.get("text")
    ]


if __name__ == "__main__":

    question = input("\nEnter your question: ")

    results = rerank(
        question,
        top_k=5
    )

    print("\n===== RESULTS =====")

    for result in results:
        print("\n--- RESULT ---")
        print("Score:", result["score"])
        print(result["text"][:1000])
