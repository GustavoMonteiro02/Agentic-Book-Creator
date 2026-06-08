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
    """LangGraph-compatible orchestration used before external LLMs are configured."""

    def gather(self, state: BookState) -> BookState:
        return gather_input(state)

    def create_book_plan(self, state: BookState) -> BookState:
        state = understand_input(state)
        state = create_strategy(state)
        return design_structure(state)

    def generate_chapter(self, state: BookState) -> BookState:
        if not state.get("structure_approved"):
            raise HumanApprovalRequired("Structure must be approved before chapter generation.")

        state = plan_chapter(state)
        state = write_chapter(state)
        state = review_chapter(state)
        state = edit_chapter(state)
        return state
