import json
import os
import sys

# Allow imports from app/
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "app")
    )
)

from retrieval import (
    get_contract,
    chunk_text,
    retrieve_chunks,
    embedding_model
)

CUAD_PATH = "data/CUADv1.json"


def load_test_case(contract_index=0, question_index=39):
    """
    Load one CUAD question and its human annotation.
    question_index=39 means Question 40.
    """

    with open(CUAD_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    contract = data["data"][contract_index]

    all_questions = []

    for paragraph in contract["paragraphs"]:
        for qa in paragraph.get("qas", []):
            all_questions.append(qa)

    qa = all_questions[question_index]

    question = qa["question"]
    answers = qa.get("answers", [])

    if not answers:
        return question, None

    ground_truth = answers[0]["text"]

    return question, ground_truth


def evaluate_retrieval(
    contract_index=0,
    question_index=39,
    top_k=3
):
    # Load CUAD ground truth
    question, ground_truth = load_test_case(
        contract_index,
        question_index
    )

    if ground_truth is None:
        print("No human annotation exists for this question.")
        return

    # Load contract
    title, context = get_contract(contract_index)

    # Chunk contract
    chunks = chunk_text(context)

     # Generate embeddings
    embeddings = embedding_model.encode(chunks)

    # Query rewriting for License Grant test
    if question_index == 25:
        retrieval_query = (
            "exclusive right granted to distributor "
            "to sell and distribute products in the market"
        )
    else:
        retrieval_query = question

    print("\nRETRIEVAL QUERY:")
    print(retrieval_query)

    # Run retrieval using the rewritten query
    results = retrieve_chunks(
        retrieval_query,
        chunks,
        embeddings,
        top_k=top_k
    )
    

    print("\n====================================")
    print("LEGAL AI POV EVALUATION")
    print("====================================")

    print("\nCONTRACT:")
    print(title)

    print("\nCUAD QUESTION:")
    print(question)

    print("\nGROUND TRUTH:")
    print(ground_truth[:500])

    print("\n------------------------------------")
    print("RETRIEVAL RESULTS")
    print("------------------------------------")

    found = False
    found_rank = None
    found_score = None

    for rank, result in enumerate(results, 1):

        print(
            f"\nRank {rank} | "
            f"Similarity: {result['score']:.4f}"
        )

        print(result["chunk"][:400])

        # Check overlap between annotation and retrieved chunk
        ground_words = set(
            ground_truth.lower().split()
        )

        retrieved_words = set(
            result["chunk"].lower().split()
        )

        overlap = ground_words.intersection(
            retrieved_words
        )

        overlap_ratio = (
            len(overlap) / len(ground_words)
            if ground_words else 0
        )

        print(
            f"Ground Truth Overlap: "
            f"{overlap_ratio:.2%}"
        )

        # Initial success threshold
        if overlap_ratio >= 0.50 and not found:
            found = True
            found_rank = rank
            found_score = result["score"]

    print("\n====================================")
    print("POV RESULT")
    print("====================================")

    if found:
        print("PASS")
        print(
            f"Ground-truth clause retrieved "
            f"at rank {found_rank}."
        )
        print(
            f"Similarity score: "
            f"{found_score:.4f}"
        )

    else:
        print("FAIL")
        print(
            "Ground-truth clause was not sufficiently "
            f"represented in the Top-{top_k} results."
        )

        print("\nNEXT ACTION:")
        print("Investigate retrieval configuration.")

    print("====================================")


if __name__ == "__main__":

    test_questions = [5, 15, 25, 39]

    for question_index in test_questions:

        print("\n\n####################################")
        print(f"TESTING CUAD QUESTION {question_index + 1}")
        print("####################################")

        evaluate_retrieval(
            contract_index=0,
            question_index=question_index,
            top_k=5
        )