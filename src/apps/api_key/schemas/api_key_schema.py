from typing import List, Optional
from pydantic import BaseModel, Field


class APIKeySchema(BaseModel):
    id: int
    key: str
    alias: Optional[str] = Field(None)
    project_id: int
    created_at: str

    class Config:
        from_attributes = True