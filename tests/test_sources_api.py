from fastapi.testclient import TestClient

from app.api.main import app


def test_source_upload_indexes_heading_aware_chunks():
    client = TestClient(app)
    project_id = _create_project(client)

    upload_response = client.post(
        f"/projects/{project_id}/sources/upload",
        json={
            "filename": "rag-notes.md",
            "content": "# RAG\nUse retrieval.\n\n# Evaluation\nMeasure recall.",
            "content_type": "text/markdown",
        },
    )
    assert upload_response.status_code == 200
    source = upload_response.json()
    assert source["filename"] == "rag-notes.md"
    assert source["chunk_count"] == 2

    sources_response = client.get(f"/projects/{project_id}/sources")
    assert sources_response.status_code == 200
    assert sources_response.json()[0]["id"] == source["id"]

    chunks_response = client.get(f"/projects/{project_id}/sources/chunks?source_id={source['id']}")
    assert chunks_response.status_code == 200
    chunks = chunks_response.json()
    assert len(chunks) == 2
    assert chunks[0]["metadata"]["heading"] == "RAG"
    assert chunks[0]["metadata"]["chunking_strategy"] == "heading_aware"

    diagnostics = client.get(f"/projects/{project_id}/diagnostics").json()
    assert diagnostics["artifact_counts"]["sources"] == 1
    assert diagnostics["artifact_counts"]["source_chunks"] == 2


def _create_project(client: TestClient) -> str:
    response = client.post(
        "/projects",
        json={
            "title": "Source Test",
            "initial_idea": "A practical book about RAG systems for automation developers.",
        },
    )
    return response.json()["project_id"]
