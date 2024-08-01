from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Request, status, Security, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

# from app import limiter

from src.config.db.mongo_management.mongo_manager import project_waitlist_collection
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
from src.apps.waitlist.schemas.waitlist_schema import WaitlistResponse, WaitlistRequest
from src.apps.api_key.service import verify_api_key
from src.config.db.postgres_management.pg_manager import get_db


api_key_header = APIKeyHeader(name="api-key", auto_error=False)

router = APIRouter(prefix="/v2")



@router.post(
    "/add",
    summary="Add to Waitlist",
    responses={
        200: {"description": "Successful response", "model": SuccessResponse},
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
async def add_to_waitlist_v2(
    request: Request,
    payload: WaitlistRequest,
    db: Session = Depends(get_db),
    key: str = Security(api_key_header),
) -> SuccessResponse:

    # TODO: verify API key
    api_key = verify_api_key(db, key)
    if not api_key:
        raise HTTPException(status_code=400, detail="Invalid API key")

    current_time = datetime.now()
    request_body = payload.model_dump()

    if project_waitlist_collection.find_one({"email": request_body.get("email"), "project_id": api_key.project_id}):
        raise HTTPException(status_code=400, detail="Email already in the waitlist")

    project_waitlist_collection.insert_one(
        {"email": request_body.get("email"), "project_id": api_key.project_id, "date_added": current_time}
    )

    return JSONResponse(
       content={"message": "Email added to waitlist successfully!"},
        status_code=status.HTTP_200_OK
    )
