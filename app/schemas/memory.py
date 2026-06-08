from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    memory_type: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=1000)
    source: str = Field(default="human", max_length=80)
    expires_at: Optional[datetime] = None


class MemoryRead(BaseModel):
    id: str
    memory_type: str
    content: str
    source: str
    created_at: datetime
    expires_at: Optional[datetime] = None
