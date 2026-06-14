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


def test_approved_project_can_generate_chapter_step_by_step():
    client = TestClient(app)
    create_response = client.post(
        "/projects",
        json={
            "title": "Agentic AI for Automation",
            "initial_idea": "Quero um livro prático sobre agentes de IA para RPA developers com código.",
        },
    )
    project_id = create_response.json()["project_id"]

    answers_response = client.post(
        f"/projects/{project_id}/answers",
        json={
            "answers": [
                {"field": "tone", "answer": "prático e conversacional"},
                {"field": "reader_level", "answer": "intermédio"},
                {"field": "preferred_structure", "answer": "do básico ao avançado por projetos"},
                {"field": "output_formats", "answer": "Markdown"},
            ]
        },
    )
    assert answers_response.status_code == 200
    assert answers_response.json()["book_structure"]["parts"]

    approval_response = client.post(
        f"/projects/{project_id}/approve-structure",
        json={"approved": True},
    )
    assert approval_response.status_code == 200

    plan_response = client.post(f"/projects/{project_id}/chapters/1/plan")
    assert plan_response.status_code == 200
    assert plan_response.json()["chapter_plans"]

    review_response = client.post(f"/projects/{project_id}/chapters/1/review")
    assert review_response.status_code == 200
    assert review_response.json()["chapter_reviews"]

    edit_response = client.post(f"/projects/{project_id}/chapters/1/edit")
    assert edit_response.status_code == 200
    assert edit_response.json()["final_chapters"][0]["chapter_number"] == 1

    runs_response = client.get(f"/projects/{project_id}/runs")
    assert runs_response.status_code == 200
    run_types = [run["run_type"] for run in runs_response.json()]
    assert "book_plan" in run_types
    assert "structure_approval" in run_types
    assert "chapter_edit" in run_types
    assert runs_response.json()[0]["llm_metadata"]["model_route"]

    diagnostics_response = client.get(f"/projects/{project_id}/diagnostics")
    assert diagnostics_response.status_code == 200
    diagnostics = diagnostics_response.json()
    assert diagnostics["estimated_total_tokens"] > 0
    assert diagnostics["llm_metadata"]["prompt_version"] == "mvp-v1"
    assert diagnostics["routing_summary"]
    assert diagnostics["quality_signals"]["has_technical_review"] is True
    assert diagnostics["debugging_checklist"]
    assert any(item["category"] == "rag_grounding" for item in diagnostics["debugging_checklist"])


def test_structure_revision_regenerates_outline_and_records_run():
    client = TestClient(app)
    create_response = client.post(
        "/projects",
        json={
            "title": "Agentic AI for Automation",
            "initial_idea": "Quero um livro prático sobre agentes de IA para RPA developers com código.",
        },
    )
    project_id = create_response.json()["project_id"]

    answers_response = client.post(
        f"/projects/{project_id}/answers",
        json={
            "answers": [
                {"field": "tone", "answer": "prático"},
                {"field": "reader_level", "answer": "intermédio"},
                {"field": "preferred_structure", "answer": "do básico ao avançado por projetos"},
            ]
        },
    )
    original_structure = answers_response.json()["book_structure"]
    assert len(original_structure["parts"]) == 2

    revision_response = client.post(
        f"/projects/{project_id}/approve-structure",
        json={"approved": False, "revision_request": "make it small"},
    )

    assert revision_response.status_code == 200
    revised_project = revision_response.json()
    assert revised_project["structure_revision_requests"] == ["make it small"]
    assert revised_project["structure_approved"] is False
    assert revised_project["book_structure"]["last_revision_applied"] == "make it small"
    assert len(revised_project["book_structure"]["parts"]) == 1
    assert "compact" in revised_project["book_structure"]["parts"][0]["chapters"][0]["goal"]

    run_types = [run["run_type"] for run in revised_project["execution_runs"]]
    assert "book_plan" in run_types
    assert "structure_revision" in run_types


def test_resubmitting_answers_preserves_previous_fields():
    client = TestClient(app)
    create_response = client.post(
        "/projects",
        json={
            "title": "Agentic AI for Automation",
            "initial_idea": "Quero um livro prático sobre agentes de IA para RPA developers com código.",
        },
    )
    project_id = create_response.json()["project_id"]

    first_response = client.post(
        f"/projects/{project_id}/answers",
        json={"answers": [{"field": "tone", "answer": "prático"}]},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/projects/{project_id}/answers",
        json={"answers": [{"field": "reader_level", "answer": "intermédio"}]},
    )

    assert second_response.status_code == 200
    saved_answers = {answer["field"]: answer["answer"] for answer in second_response.json()["user_answers"]}
    assert saved_answers["tone"] == "prático"
    assert saved_answers["reader_level"] == "intermédio"
