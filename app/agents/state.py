from typing import Any, Dict, List, TypedDict


class BookState(TypedDict, total=False):
    project_id: str
    initial_user_idea: str
    raw_user_inputs: List[str]
    input_questions: List[Dict[str, Any]]
    user_answers: List[Dict[str, Any]]
    book_requirements: Dict[str, Any]
    missing_information: List[str]
    book_strategy: Dict[str, Any]
    book_structure: Dict[str, Any]
    chapter_template: Dict[str, Any]
    structure_approved: bool
    structure_revision_requests: List[str]
    current_chapter_number: int
    chapter_plans: List[Dict[str, Any]]
    chapter_drafts: List[Dict[str, Any]]
    chapter_reviews: List[Dict[str, Any]]
    final_chapters: List[Dict[str, Any]]
    user_feedback: List[Dict[str, Any]]
    project_memory: List[Dict[str, Any]]
    execution_runs: List[Dict[str, Any]]
    status: str
    errors: List[Dict[str, Any]]
