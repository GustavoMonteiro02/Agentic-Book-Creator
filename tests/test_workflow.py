from app.agents.graph import HumanApprovalRequired, SimpleBookWorkflow


def test_workflow_requires_structure_approval_before_chapter_generation():
    workflow = SimpleBookWorkflow()
    state = {
        "project_id": "test",
        "initial_user_idea": "A practical book about AI agents for automation developers.",
        "user_answers": [],
        "structure_approved": False,
    }

    try:
        workflow.generate_chapter(state)
    except HumanApprovalRequired:
        assert True
    else:
        assert False


def test_workflow_generates_final_chapter_after_approval():
    workflow = SimpleBookWorkflow()
    assert workflow.chapter_graph is not None
    state = {
        "project_id": "test",
        "initial_user_idea": "A practical book about AI agents for automation developers.",
        "user_answers": [{"field": "output_formats", "answer": "Markdown"}],
        "structure_approved": True,
        "chapter_plans": [],
        "chapter_drafts": [],
        "chapter_reviews": [],
        "final_chapters": [],
        "current_chapter_number": 1,
    }

    state = workflow.create_book_plan(state)
    state["structure_approved"] = True
    result = workflow.generate_chapter(state)

    assert result["status"] == "chapter_finalized"
    assert result["final_chapters"][0]["chapter_number"] == 1
