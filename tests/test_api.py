from fastapi.testclient import TestClient

from app.api.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_project_to_questions_flow():
    client = TestClient(app)
    create_response = client.post(
        "/projects",
        json={
            "title": "Agentic AI for Automation",
            "initial_idea": "Quero um livro prático sobre agentes de IA para RPA developers com código.",
        },
    )
    assert create_response.status_code == 200
    project_id = create_response.json()["project_id"]

    questions_response = client.post(f"/projects/{project_id}/questions")
    assert questions_response.status_code == 200
    assert "input_questions" in questions_response.json()
