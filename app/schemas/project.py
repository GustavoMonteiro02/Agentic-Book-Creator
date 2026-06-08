from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    initial_idea: str = Field(min_length=10)


class ProjectRead(BaseModel):
    id: str
    title: str
    initial_idea: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
