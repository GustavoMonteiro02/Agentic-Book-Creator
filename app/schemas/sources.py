from pydantic import BaseModel, Field


class SourceUpload(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    content_type: str = Field(default="text/markdown", max_length=100)


class SourceRead(BaseModel):
    id: str
    filename: str
    content_type: str
    chunk_count: int
    created_at: str
