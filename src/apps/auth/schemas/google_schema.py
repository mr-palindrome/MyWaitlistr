from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

class GoogleInputSchema(BaseModel):
    code: str = Field(..., description="Authorization code from Google")
    error: Optional[str] = Field(None, description="Error parameter from Google")


    