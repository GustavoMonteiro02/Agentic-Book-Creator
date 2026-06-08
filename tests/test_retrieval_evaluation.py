from app.evaluation.retrieval import RetrievalCase, evaluate_retrieval, reciprocal_rank


def test_evaluate_retrieval_scores_ranked_results():
    cases = [
        RetrievalCase(
            query="What changed in the embedding model?",
            expected_document_ids={"doc-2"},
            retrieved_document_ids=["doc-1", "doc-2", "doc-3"],
        ),
        RetrievalCase(
            query="How do we approve book structure?",
            expected_document_ids={"doc-4"},
            retrieved_document_ids=["doc-4", "doc-5"],
        ),
    ]

    result = evaluate_retrieval(cases, k=2)

    assert result["case_count"] == 2
    assert result["precision_at_k"] == 0.5
    assert result["recall_at_k"] == 1.0
    assert result["hit_rate_at_k"] == 1.0
    assert result["mrr"] == 0.75


def test_reciprocal_rank_returns_zero_without_hit():
    assert reciprocal_rank(["doc-1", "doc-2"], {"doc-3"}) == 0.0
