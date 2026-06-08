from pydantic import BaseModel


class BookStrategy(BaseModel):
    suggested_title: str
    subtitle: str
    book_promise: str
    target_reader: str
    learning_outcomes: list[str]
    teaching_approach: str
    style_guide: str
    difficulty_progression: str
    primary_reader_value: str
