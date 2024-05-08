from pydantic import BaseModel


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
    error: str = "Bad Request"
