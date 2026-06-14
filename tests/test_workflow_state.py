from frontend.workflow_state import next_action, workflow_progress, workflow_steps


def test_workflow_progress_is_empty_without_project():
    assert workflow_progress(None) == 0.0
    assert next_action(None) == "Create a project to start the LangGraph workflow."


def test_workflow_progress_tracks_completed_steps():
    project = {
        "project_id": "book-1",
        "input_questions": [{"question": "Who is it for?"}],
        "book_requirements": {"audience": "developers"},
        "book_strategy": {"positioning": "practical"},
        "book_structure": {"chapters": []},
        "structure_approved": True,
    }

    steps = workflow_steps(project)

    assert [step["complete"] for step in steps] == [True, True, True, True, True, True, False]
    assert workflow_progress(project) == 6 / 7
    assert next_action(project) == "Generate chapter 1 from the approved structure."


def test_next_action_points_to_approval_after_structure_generation():
    project = {
        "project_id": "book-1",
        "input_questions": [{"question": "Who is it for?"}],
        "book_requirements": {"audience": "developers"},
        "book_strategy": {"positioning": "practical"},
        "book_structure": {"chapters": []},
    }

    assert next_action(project) == "Review and approve the book structure."


def test_questions_are_complete_when_plan_already_exists():
    project = {
        "project_id": "book-1",
        "book_requirements": {"audience": "developers"},
        "book_strategy": {"positioning": "practical"},
        "book_structure": {"chapters": []},
    }

    steps = workflow_steps(project)

    assert steps[1] == {"label": "Questions", "complete": True}
    assert next_action(project) == "Review and approve the book structure."
