from pydantic import BaseModel, Field


class WaitlistRequest(BaseModel):
    email: str = Field(
        ...,
        example="mywaitlistr@nayandas.dev",
        description="End date for the screening to be complete (only applicable for ongoing monitoring).",
    )


class WaitlistResponse(BaseModel):
    message: str = Field(
        ...,
        example="Email added to waitlist successfully!",
        description="A message describing the result.",
    )
