from pydantic import BaseModel, Field
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
    _id: str
    project_id: int

    class Config:
        from_attributes = True
