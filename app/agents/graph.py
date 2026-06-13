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


class HumanApprovalRequired(Exception):
    """Raised when the workflow reaches the structure approval gate."""


class SimpleBookWorkflow:
    """LangGraph-backed orchestration for the core creation workflow."""

    def __init__(self) -> None:
        self.gather_graph = _compile_linear_graph([("gather_input", gather_input)])
        self.book_plan_graph = _compile_linear_graph(
            [
                ("understand_input", understand_input),
                ("create_strategy", create_strategy),
                ("design_structure", design_structure),
            ]
        )
        self.chapter_graph = _compile_linear_graph(
            [
                ("plan_chapter", plan_chapter),
                ("write_chapter", write_chapter),
                ("review_chapter", review_chapter),
                ("edit_chapter", edit_chapter),
            ]
        )

    def gather(self, state: BookState) -> BookState:
        return self.gather_graph.invoke(dict(state))

    def create_book_plan(self, state: BookState) -> BookState:
        return self.book_plan_graph.invoke(dict(state))

    def generate_chapter(self, state: BookState) -> BookState:
        if not state.get("structure_approved"):
            raise HumanApprovalRequired("Structure must be approved before chapter generation.")

        return self.chapter_graph.invoke(dict(state))


def _compile_linear_graph(nodes):
    graph = StateGraph(BookState)
    for node_name, node_fn in nodes:
        graph.add_node(node_name, node_fn)

    graph.set_entry_point(nodes[0][0])
    for index, (node_name, _) in enumerate(nodes):
        next_index = index + 1
        graph.add_edge(node_name, nodes[next_index][0] if next_index < len(nodes) else END)

    return graph.compile()
