from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.api.main import app


def test_project_memory_can_be_added_listed_and_deleted():
    client = TestClient(app)
    project_id = _create_project(client)

    add_response = client.post(
        f"/projects/{project_id}/memory",
        json={
            "memory_type": "style_preference",
            "content": "User prefers practical examples with Python code.",
            "source": "human",
        },
    )
    assert add_response.status_code == 200
    memory_id = add_response.json()["id"]

    list_response = client.get(f"/projects/{project_id}/memory")
    assert list_response.status_code == 200
    assert list_response.json()[0]["content"] == "User prefers practical examples with Python code."

    diagnostics_response = client.get(f"/projects/{project_id}/diagnostics")
    assert diagnostics_response.json()["artifact_counts"]["memory_items"] == 1

    delete_response = client.delete(f"/projects/{project_id}/memory/{memory_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}

    assert client.get(f"/projects/{project_id}/memory").json() == []


def test_project_memory_filters_expired_items_by_default():
    client = TestClient(app)
    project_id = _create_project(client)
    expired_at = (datetime.utcnow() - timedelta(days=1)).isoformat()

    add_response = client.post(
        f"/projects/{project_id}/memory",
        json={
            "memory_type": "temporary_instruction",
            "content": "Use a shorter tone for this week.",
            "expires_at": expired_at,
        },
    )
    assert add_response.status_code == 200

    assert client.get(f"/projects/{project_id}/memory").json() == []
    assert len(client.get(f"/projects/{project_id}/memory?include_expired=true").json()) == 1


def _create_project(client: TestClient) -> str:
    response = client.post(
        "/projects",
        json={
            "title": "Memory Test",
            "initial_idea": "A practical book about reliable AI engineering workflows.",
        },
    )
    return response.json()["project_id"]
