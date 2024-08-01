from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from .request_schema import ProjectSchema

class ProjectResponseSchema(ProjectSchema):
    id: int
    project_id: str 
    limit: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        