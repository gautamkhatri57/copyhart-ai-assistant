from sentence_transformers import CrossEncoder
from rag.retriever import retrieve


print("Loading reranker model...")

reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank(question, top_k=5):

    # Retrieve more candidates first
    retrieved_results = retrieve(
        question,
        top_k=10
    )

    if not retrieved_results:
        return []

    # Create question-document pairs
    pairs = [
        (question, result["text"])
        for result in retrieved_results
    ]

    # Calculate reranking scores
    scores = reranker_model.predict(pairs)

    reranked_results = []

    for result, score in zip(
        retrieved_results,
        scores
    ):

        reranked_results.append({
            "score": float(score),
            "text": result["text"]
        })

    # Highest score first
    reranked_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return reranked_results[:top_k]


if __name__ == "__main__":

    question = input("\nEnter your question: ")

    results = rerank(
        question,
        top_k=5
    )

    print("\n===== RERANKED RESULTS =====")

    for result in results:

        print("\n--- RESULT ---")
        print("Score:", result["score"])
        print(result["text"][:1000])