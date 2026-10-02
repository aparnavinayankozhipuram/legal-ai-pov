from retrieval import (
    get_contract,
    chunk_text,
    retrieve_chunks,
    embedding_model,
    generate_legal_answer
)


def run_legal_ai_pipeline(question, contract_index=0):
    """
    Orchestrates the complete Legal AI workflow.
    """

    print("\n[ORCHESTRATOR] Starting Legal AI workflow")

    # STEP 1 — Load contract
    print("[1] Loading contract...")

    title, context = get_contract(contract_index)

    print(f"    Contract: {title}")


    # STEP 2 — Chunk contract
    print("[2] Chunking contract...")

    chunks = chunk_text(context)

    print(f"    Created {len(chunks)} chunks")


    # STEP 3 — Generate embeddings
    print("[3] Generating embeddings...")

    embeddings = embedding_model.encode(chunks)

    print(f"    Generated {len(embeddings)} embeddings")


    # STEP 4 — Retrieve evidence
    print("[4] Retrieving relevant legal clauses...")

    results = retrieve_chunks(
        question,
        chunks,
        embeddings,
        top_k=3
    )

    for i, result in enumerate(results, 1):
        print(
            f"    Evidence {i}: "
            f"score={result['score']:.4f}"
        )


    # STEP 5 — Call LLM
    print("[5] Sending retrieved evidence to Llama 3.2...")

    answer = generate_legal_answer(
        question,
        results
    )


    # STEP 6 — Return structured result
    print("[6] Workflow completed.")

    return {
        "contract": title,
        "question": question,
        "retrieved_evidence": results,
        "answer": answer
    }


if __name__ == "__main__":

    question = input(
        "\nAsk a legal contract question: "
    )

    result = run_legal_ai_pipeline(question)

    print("\n================================")
    print("LEGAL AI ANSWER")
    print("================================")

    print(result["answer"])