from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Section(BaseModel):
    title: str
    purpose: str


class ChapterStructure(BaseModel):
    chapter_number: int
    title: str
    goal: str
    sections: list[Section]
    practical_example: str
    mini_project: str
    exercises: list[str]


class BookPart(BaseModel):
    part_title: str
    part_goal: str
    chapters: list[ChapterStructure]


class BookStructure(BaseModel):
    book_title: str
    parts: list[BookPart]


class ApproveStructureRequest(BaseModel):
    approved: bool
    revision_request: Optional[str] = None
