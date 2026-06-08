from pydantic import BaseModel


class ChapterPlan(BaseModel):
    chapter_number: int
    title: str
    goal: str
    key_concepts: list[str]
    pedagogical_sequence: list[str]
    examples: list[str]
    analogies: list[str]
    code_required: list[str]
    exercises: list[str]
    quality_criteria: list[str]


class ChapterOutput(BaseModel):
    chapter_number: int
    title: str
    markdown: str
