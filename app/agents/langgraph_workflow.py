from langgraph.graph import END, StateGraph

from app.agents.book_strategy_agent import create_strategy
from app.agents.chapter_planner_agent import plan_chapter
from app.agents.chapter_writer_agent import write_chapter
from app.agents.editor_agent import edit_chapter
from app.agents.input_gathering_agent import gather_input
from app.agents.input_understanding_agent import understand_input
from app.agents.state import BookState
from app.agents.structure_designer_agent import design_structure
from app.agents.technical_reviewer_agent import review_chapter


def build_book_graph():
    graph = StateGraph(BookState)

    graph.add_node("gather_input", gather_input)
    graph.add_node("understand_input", understand_input)
    graph.add_node("create_strategy", create_strategy)
    graph.add_node("design_structure", design_structure)
    graph.add_node("plan_chapter", plan_chapter)
    graph.add_node("write_chapter", write_chapter)
    graph.add_node("review_chapter", review_chapter)
    graph.add_node("edit_chapter", edit_chapter)

    graph.set_entry_point("gather_input")
    graph.add_conditional_edges(
        "gather_input",
        _route_after_input_gathering,
        {
            "pause_for_input": END,
            "continue": "understand_input",
        },
    )
    graph.add_edge("understand_input", "create_strategy")
    graph.add_edge("create_strategy", "design_structure")
    graph.add_conditional_edges(
        "design_structure",
        _route_after_structure,
        {
            "pause_for_approval": END,
            "continue": "plan_chapter",
        },
    )
    graph.add_edge("plan_chapter", "write_chapter")
    graph.add_edge("write_chapter", "review_chapter")
    graph.add_conditional_edges(
        "review_chapter",
        _route_after_review,
        {
            "revise": "write_chapter",
            "continue": "edit_chapter",
        },
    )
    graph.add_edge("edit_chapter", END)

    return graph.compile()


def _route_after_input_gathering(state: BookState) -> str:
    return "pause_for_input" if state.get("input_questions") else "continue"


def _route_after_structure(state: BookState) -> str:
    return "continue" if state.get("structure_approved") else "pause_for_approval"


def _route_after_review(state: BookState) -> str:
    reviews = state.get("chapter_reviews", [])
    if not reviews:
        return "continue"

    latest_review = reviews[-1]
    has_high_severity_issue = any(issue.get("severity") == "high" for issue in latest_review.get("issues", []))
    return "revise" if has_high_severity_issue else "continue"
