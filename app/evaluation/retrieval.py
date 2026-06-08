from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalCase:
    query: str
    expected_document_ids: set[str]
    retrieved_document_ids: list[str]


def precision_at_k(retrieved_document_ids: list[str], expected_document_ids: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    top_k = retrieved_document_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for document_id in top_k if document_id in expected_document_ids)
    return hits / len(top_k)


def recall_at_k(retrieved_document_ids: list[str], expected_document_ids: set[str], k: int) -> float:
    if not expected_document_ids or k <= 0:
        return 0.0
    top_k = retrieved_document_ids[:k]
    hits = sum(1 for document_id in top_k if document_id in expected_document_ids)
    return hits / len(expected_document_ids)


def hit_rate_at_k(retrieved_document_ids: list[str], expected_document_ids: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    return 1.0 if any(document_id in expected_document_ids for document_id in retrieved_document_ids[:k]) else 0.0


def reciprocal_rank(retrieved_document_ids: list[str], expected_document_ids: set[str]) -> float:
    for index, document_id in enumerate(retrieved_document_ids, start=1):
        if document_id in expected_document_ids:
            return 1 / index
    return 0.0


def evaluate_retrieval(cases: list[RetrievalCase], k: int = 5) -> dict:
    if not cases:
        return {
            "case_count": 0,
            "k": k,
            "precision_at_k": 0.0,
            "recall_at_k": 0.0,
            "hit_rate_at_k": 0.0,
            "mrr": 0.0,
        }

    precision = sum(precision_at_k(case.retrieved_document_ids, case.expected_document_ids, k) for case in cases)
    recall = sum(recall_at_k(case.retrieved_document_ids, case.expected_document_ids, k) for case in cases)
    hit_rate = sum(hit_rate_at_k(case.retrieved_document_ids, case.expected_document_ids, k) for case in cases)
    mrr = sum(reciprocal_rank(case.retrieved_document_ids, case.expected_document_ids) for case in cases)

    case_count = len(cases)
    return {
        "case_count": case_count,
        "k": k,
        "precision_at_k": round(precision / case_count, 4),
        "recall_at_k": round(recall / case_count, 4),
        "hit_rate_at_k": round(hit_rate / case_count, 4),
        "mrr": round(mrr / case_count, 4),
    }
