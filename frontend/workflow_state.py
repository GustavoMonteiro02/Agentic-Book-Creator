from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowStep:
    label: str
    is_complete: Callable[[dict], bool]


WORKFLOW_STEPS = (
    WorkflowStep("Project", lambda project: bool(project.get("project_id"))),
    WorkflowStep("Questions", lambda project: bool(project.get("input_questions"))),
    WorkflowStep("Brief", lambda project: bool(project.get("book_requirements"))),
    WorkflowStep("Strategy", lambda project: bool(project.get("book_strategy"))),
    WorkflowStep("Structure", lambda project: bool(project.get("book_structure"))),
    WorkflowStep("Approved", lambda project: bool(project.get("structure_approved"))),
    WorkflowStep("Chapter", lambda project: bool(project.get("final_chapters"))),
)


def workflow_steps(project: dict | None) -> list[dict[str, bool | str]]:
    project = project or {}
    return [{"label": step.label, "complete": step.is_complete(project)} for step in WORKFLOW_STEPS]


def workflow_progress(project: dict | None) -> float:
    steps = workflow_steps(project)
    if not steps:
        return 0.0
    return sum(1 for step in steps if step["complete"]) / len(steps)


def next_action(project: dict | None) -> str:
    project = project or {}
    if not project.get("project_id"):
        return "Create a project to start the LangGraph workflow."
    if not project.get("input_questions"):
        return "Generate adaptive questions from the initial book idea."
    if not project.get("book_requirements"):
        return "Answer the adaptive questions so Gemini can build the brief, strategy, and structure."
    if not project.get("structure_approved"):
        return "Review and approve the book structure."
    if not project.get("final_chapters"):
        return "Generate chapter 1 from the approved structure."
    return "Export the draft or continue generating chapters."
