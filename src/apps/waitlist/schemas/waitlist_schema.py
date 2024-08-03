from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WaitlistRequest(BaseModel):
    email: str = Field(
        ...,
        example="mywaitlistr@nayandas.dev",
        description="End date for the screening to be complete (only applicable for ongoing monitoring).",
    )


class WaitlistResponse(BaseModel):
    email: str
    date_added: str
    _id: Optional[str] = None
    project_id: Optional[int] = None

    class Config:
        from_attributes = True
