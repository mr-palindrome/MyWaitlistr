from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

# from app import limiter
from src.config.db.mongo_management.mongo_manager import waitlist_collection
from src.apps.base.schemas.reponse_types import (
    SuccessResponse,
    ResponseSchema,
    BadGatewayResponse,
    BadRequestResponse,
    InternalServerErrorResponse,
    # NotAuthorizedReponse,
    ServiceUnavailableResponse,
    TooManyRequestsReponse,
)
from src.apps.waitlist.schemas.waitlist_schema import WaitlistRequest

api_key_header = APIKeyHeader(name="api-key", auto_error=False)

router = APIRouter(prefix="/v1")

@router.post(
    "/add",
    # response_model=ResponseSchema,
    summary="Add to Waitlist",
    responses={
        200: {"description": "Successful response", "model": ResponseSchema},
        400: {"description": "Bad request", "model": BadRequestResponse},
        429: {"description": "Too many requests", "model": TooManyRequestsReponse},
        500: {
            "description": "Internal Server Error",
            "model": InternalServerErrorResponse,
        },
        502: {"description": "Bad Gateway", "model": BadGatewayResponse},
        503: {
            "description": "Service Unavailable",
            "model": ServiceUnavailableResponse,
        },
    },
    tags=["Waitlist"],
)
# @limiter.limit("20/minute")
async def add_to_waitlist(
    request: Request,
    payload: WaitlistRequest,
):

    current_time = datetime.now()
    request_body = payload.model_dump()

    if waitlist_collection.find_one({"email": request_body.get("email")}):
        raise HTTPException(status_code=400, detail="Email already in the waitlist")

    waitlist_collection.insert_one(
        {"email": request_body.get("email"), "date_added": current_time}
    )

    return JSONResponse(
        status_code=200,
        content={"message": "Email added to waitlist successfully!"}
    )
