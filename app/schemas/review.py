from pydantic import BaseModel


class ReviewIssue(BaseModel):
    type: str
    location: str
    comment: str
    severity: str


class TechnicalReview(BaseModel):
    chapter_number: int
    review_type: str
    technical_score: int
    approved: bool
    issues: list[ReviewIssue]
    improvement_suggestions: list[str]
