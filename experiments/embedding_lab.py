"""Small experiment for understanding text embeddings and cosine similarity."""

from __future__ import annotations

from industrial_copilot.embeddings.similarity import cosine_similarity

from sentence_transformers import SentenceTransformer

SENTENCES = [

    "The hydraulic pump requires maintenance.",

    "The hydraulic pump needs to be serviced.",

    "The pump should undergo a routine inspection.",

    "The employee cafeteria serves lunch at noon.",

    "HX-417 indicates low hydraulic pressure.",

    "HX-471 indicates excessive hydraulic oil temperature.",

]

QUERY = "When should the hydraulic pump be maintained?"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def main() -> None:

    """Generate embeddings and rank sentences by similarity to the query."""

    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    sentence_embeddings = model.encode(

        SENTENCES,

        convert_to_numpy=True,

    )

    query_embedding = model.encode(

        QUERY,

        convert_to_numpy=True,

    )

    print("\nEmbedding information")

    print("---------------------")

    print(f"Number of sentences: {len(SENTENCES)}")

    print(f"Embedding matrix shape: {sentence_embeddings.shape}")

    print(f"Query embedding shape: {query_embedding.shape}")

    print(f"First 10 values of the first embedding:\n{sentence_embeddings[0][:10]}")

    scored_sentences: list[tuple[float, str]] = []

    for sentence, embedding in zip(

        SENTENCES,

        sentence_embeddings,

        strict=True,

    ):

        score = cosine_similarity(query_embedding, embedding)

        scored_sentences.append((score, sentence))

    scored_sentences.sort(key=lambda item: item[0], reverse=True)

    print("\nQuery")

    print("-----")

    print(QUERY)

    print("\nSentences ranked by cosine similarity")

    print("-------------------------------------")

    for rank, (score, sentence) in enumerate(scored_sentences, start=1):

        print(f"{rank}. {score:.4f} — {sentence}")

if __name__ == "__main__":

    main()
