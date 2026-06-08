from fastapi.testclient import TestClient

from app.api.main import app


def test_retrieval_evaluation_endpoint_scores_cases():
    client = TestClient(app)
    project_id = _create_project(client)

    response = client.post(
        f"/projects/{project_id}/evaluate/retrieval",
        json={
            "k": 2,
            "cases": [
                {
                    "query": "How do embeddings migrate?",
                    "expected_document_ids": ["doc-2"],
                    "retrieved_document_ids": ["doc-1", "doc-2"],
                },
                {
                    "query": "How do checkpoints work?",
                    "expected_document_ids": ["doc-3"],
                    "retrieved_document_ids": ["doc-3", "doc-4"],
                },
            ],
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["project_id"] == project_id
    assert result["precision_at_k"] == 0.5
    assert result["recall_at_k"] == 1.0
    assert result["mrr"] == 0.75


def _create_project(client: TestClient) -> str:
    response = client.post(
        "/projects",
        json={
            "title": "Eval Test",
            "initial_idea": "A practical book about RAG evaluation for developers.",
        },
    )
    return response.json()["project_id"]
