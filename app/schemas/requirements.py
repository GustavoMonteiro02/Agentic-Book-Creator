from pydantic import BaseModel


class BookRequirements(BaseModel):
    main_topic: str
    target_audience: str
    reader_level: str
    book_goal: str
    tone: str
    technical_depth: str
    content_preferences: list[str]
    required_topics: list[str]
    topics_to_avoid: list[str]
    preferred_structure: str
    chapter_format: list[str]
    output_formats: list[str]
