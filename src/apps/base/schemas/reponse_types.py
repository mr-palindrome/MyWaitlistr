from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Optional, Generic, TypeVar

T = TypeVar("T")


class SuccessResponse(BaseModel):
    msg: str = "Success"

class CreatedResponse(BaseModel):
    msg: str = "Created"
    
class NotAuthorizedReponse(BaseModel):
    msg: str = "Not Authorized"


class TooManyRequestsReponse(BaseModel):
    error: str = "Rate limit exceeded"


class InternalServerErrorResponse(BaseModel):
    error: str = "Internal Server Error"


class BadGatewayResponse(BaseModel):
    detail: str = "Bad Gateway"


class ServiceUnavailableResponse(BaseModel):
    msg: str = "Service Unavailable"


class BadRequestResponse(BaseModel):
    error: str


class ResponseSchema(GenericModel, Generic[T]):
    message: str
    data: Optional[T]


class PaginatedResponseSchema(GenericModel, Generic[T]):
    message: str
    data: Optional[T]
    total: int