from uuid import uuid4
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List

from src.config.db.postgres_management.pg_manager import get_db, engine
from src.apps.api_key.models import APIKey
from src.apps.api_key.schemas.api_key_schema import APIKeySchema
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
from src.apps.api_key.service import get_project_api_keys, verify_api_key, create_api_key_response_data, create_api_key, verify_project_api_key, update_api_key_alias, delete_api_key
from src.apps.projects.service import get_project_by_project_id
from src.apps.auth.utils.password import oauth2_scheme
from src.apps.auth.service import get_current_user

APIKey.__table__.create(bind=engine, checkfirst=True)

router = APIRouter(prefix="/v1")


@router.get(
    "/{project_uiid}/list",
    summary="Get all API keys",
    responses={
        200: {"description": "Successful response", "model": ResponseSchema[List[APIKeySchema]]},
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
    tags=["API Keys"],
)
async def get_api_keys(
    project_uiid: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    user = await get_current_user(db=db, token=token)
    project = get_project_by_project_id(db, project_uiid, user.id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found",
        )
    api_keys = get_project_api_keys(db, project.id)

    api_key_data = [create_api_key_response_data(api_key) for api_key in api_keys]

    response = ResponseSchema[List[APIKeySchema]](
        data=api_key_data,
        message="API keys retrieved successfully",
    )

    return JSONResponse(
        content=response.dict(),
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/{project_uiid}/create",
    summary="Create an API key",
    responses={
        201: {"description": "Successful response", "model": ResponseSchema[APIKeySchema]},
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
    tags=["API Keys"],
)
async def add_api_key(
    project_uiid: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    user = await get_current_user(db=db, token=token)
    project = get_project_by_project_id(db, project_uiid, user.id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found",
        )

    api_key = create_api_key(db, project.id, str(uuid4()))

    api_key_data = create_api_key_response_data(api_key)

    response = ResponseSchema[APIKeySchema](
        data=api_key_data,
        message="API key created successfully",
    )

    return JSONResponse(
        content=response.dict(),
        status_code=status.HTTP_201_CREATED,
    )

@router.patch(
    "/{project_uiid}/{pk}/alias",
    summary="Update an API key",
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
    tags=["API Keys"],
)
async def update_api_key(
    request: Request,
    project_uiid: str,
    pk: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    alias = request.query_params.get('alias')
    user = await get_current_user(db=db, token=token)
    project = get_project_by_project_id(db, project_uiid, user.id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found",
        )

    api_key = verify_project_api_key(db, pk, project.id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key not found",
        )
    
    api_key = update_api_key_alias(db, api_key, alias)

    return JSONResponse(
        content={"message": "API key updated successfully"},
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    "/{project_uiid}/{pk}",
    summary="Delete an API key",
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
    tags=["API Keys"],
)
async def delete_api_key_endpoint(
    project_uiid: str,
    pk: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    user = await get_current_user(db=db, token=token)
    project = get_project_by_project_id(db, project_uiid, user.id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found",
        )

    api_key = verify_project_api_key(db, pk, project.id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key not found",
        )

    delete_api_key(db, api_key)

    return JSONResponse(
        content={"message": "API key deleted successfully"},
        status_code=status.HTTP_200_OK,
    )