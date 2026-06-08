from app.agents.langgraph_workflow import (
    _route_after_input_gathering,
    _route_after_review,
    _route_after_structure,
    build_book_graph,
)


def test_langgraph_builder_compiles():
    graph = build_book_graph()
    assert graph is not None


def test_langgraph_routes_pause_for_missing_input_and_approval():
    assert _route_after_input_gathering({"input_questions": [{"question": "Tone?"}]}) == "pause_for_input"
    assert _route_after_input_gathering({"input_questions": []}) == "continue"
    assert _route_after_structure({"structure_approved": False}) == "pause_for_approval"
    assert _route_after_structure({"structure_approved": True}) == "continue"


def test_langgraph_review_route_revises_on_high_severity_issue():
    state = {
        "chapter_reviews": [
            {
                "issues": [
                    {"severity": "high", "comment": "Incorrect claim"},
                ]
            }
        ]
    }
    assert _route_after_review(state) == "revise"
