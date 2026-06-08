from pydantic import BaseModel, Field


class UserAnswer(BaseModel):
    field: str
    answer: str = Field(min_length=1)


class UserAnswersRequest(BaseModel):
    answers: list[UserAnswer]


class InputQuestion(BaseModel):
    field: str
    question: str
    purpose: str
