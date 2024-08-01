from typing import List, Optional
from pydantic import BaseModel, Field

class ProjectSchema(BaseModel):
    name: str
    description: str
    url: Optional[str] = None

    class Config:
        from_attributes = True

class CreateProjectSchema(BaseModel):

    name: str
    description: str
    url: Optional[str] = None
    limit: Optional[int] = 50

    class Config:
        from_attributes = True