from fastapi.testclient import TestClient

from app.api.main import app


def test_checkpoints_are_created_and_can_be_restored():
    client = TestClient(app)
    create_response = client.post(
        "/projects",
        json={
            "title": "Checkpoint Test",
            "initial_idea": "A practical book about agentic workflows for developers.",
        },
    )
    project_id = create_response.json()["project_id"]

    answers_response = client.post(
        f"/projects/{project_id}/answers",
        json={"answers": [{"field": "output_formats", "answer": "Markdown"}]},
    )
    assert answers_response.status_code == 200

    checkpoints_response = client.get(f"/projects/{project_id}/checkpoints")
    assert checkpoints_response.status_code == 200
    checkpoints = checkpoints_response.json()
    assert checkpoints[0]["node_name"] == "book_plan"

    approval_response = client.post(f"/projects/{project_id}/approve-structure", json={"approved": True})
    assert approval_response.json()["structure_approved"] is True

    restore_response = client.post(f"/projects/{project_id}/checkpoints/{checkpoints[0]['id']}/restore")
    assert restore_response.status_code == 200
    restored = restore_response.json()
    assert restored["structure_approved"] is False
    assert restored["status"] == "restored:book_plan"
