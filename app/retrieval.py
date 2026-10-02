import json
import numpy as np
import ollama

from sentence_transformers import SentenceTransformer

CUAD_PATH = "data/CUADv1.json"

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def load_cuad():
    with open(CUAD_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_contract(index=0):
    data = load_cuad()

    contract = data["data"][index]

    title = contract["title"]
    context = contract["paragraphs"][0]["context"]

    return title, context


def chunk_text(text, chunk_size=1500, overlap=300):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks


def retrieve_chunks(query, chunks, embeddings, top_k=3):
    # Convert question into an embedding
    query_embedding = embedding_model.encode(query)

    # Cosine similarity
    similarities = np.dot(
        embeddings,
        query_embedding
    ) / (
        np.linalg.norm(embeddings, axis=1)
        * np.linalg.norm(query_embedding)
    )

    # Get highest scoring chunks
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []

    for index in top_indices:
        results.append(
            {
                "chunk": chunks[index],
                "score": similarities[index]
            }
        )

    return results
def generate_legal_answer(query, results):
    context = "\n\n".join(
        result["chunk"] for result in results
    )

    prompt = f"""
You are a legal contract analysis assistant.

Answer the question using ONLY the contract text below.

Do not invent information.
If the answer is not contained in the text, say that there
is not enough information.

CONTRACT TEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

if __name__ == "__main__":

    title, context = get_contract()

    chunks = chunk_text(context)

    embeddings = embedding_model.encode(chunks)

    print("\nCONTRACT TITLE:")
    print(title)

    print("\nTOTAL CHARACTERS:")
    print(len(context))

    print("\nTOTAL CHUNKS:")
    print(len(chunks))

    print("\nTOTAL EMBEDDINGS:")
    print(len(embeddings))

    print("\nEMBEDDING DIMENSIONS:")
    print(len(embeddings[0]))

    # Test semantic retrieval
    query = "What are the termination provisions?"

    results = retrieve_chunks(
        query,
        chunks,
        embeddings,
        top_k=5
    )

    print("\nQUERY:")
    print(query)

    print("\nTOP RETRIEVED CHUNKS:")

    for i, result in enumerate(results, 1):
        print(f"\n--- RESULT {i} ---")
        print(f"Similarity Score: {result['score']:.4f}")
        print(result["chunk"][:800])

    answer = generate_legal_answer(query, results)

    print("\n==============================")
    print("LEGAL AI ANSWER")
    print("==============================")

    print(answer)
        