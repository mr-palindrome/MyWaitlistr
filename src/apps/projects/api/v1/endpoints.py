from uuid import uuid4
import json
from fastapi import APIRouter, HTTPException, Request, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import Annotated, Optional, List

from src.config.db.mongo_management.mongo_manager import project_waitlist_collection
from src.config.db.postgres_management.pg_manager import get_db, engine
from src.config.db.redis_management.redis_manager import get_redis
from src.apps.projects.schemas.request_schema import ProjectSchema, CreateProjectSchema
from src.apps.projects.schemas.response_schema import ProjectResponseSchema
from src.apps.projects.service import (
    get_project_by_name,
    get_project_by_id,
    get_project_by_project_id,
    get_all_projects,
    create_project,
    update_project,
    create_project_response_data,
    update_project_by_project_id,
    download_waitlist,
    EXTENSION_TYPES
)
from src.apps.base.schemas.reponse_types import (
    SuccessResponse,
    ResponseSchema,
    PaginatedResponseSchema,
    BadGatewayResponse,
    BadRequestResponse,
    InternalServerErrorResponse,
    # NotAuthorizedReponse,
    ServiceUnavailableResponse,
    TooManyRequestsReponse,
)
from src.apps.waitlist.schemas.waitlist_schema import WaitlistResponse
from src.apps.projects.models import Project
from src.apps.auth.utils.password import oauth2_scheme
from src.apps.auth.service import get_current_user

Project.__table__.create(bind=engine, checkfirst=True)

router = APIRouter(prefix="/v1")

@router.get(
    "/projects",
    summary="Get all projects",
    responses={
        200: {"description": "Successful response", "model": ResponseSchema[List[ProjectResponseSchema]]},
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
    tags=["Projects"],
)
async def get_projects(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):

    user = await get_current_user(db=db, token=token)
    projects = get_all_projects(db, user.id)

    project_data = [create_project_response_data(project) for project in projects]

    response = ResponseSchema[List[ProjectResponseSchema]](
        data=project_data,
        message="Projects retrieved successfully",
    )

    return JSONResponse(content=response.dict(), status_code=status.HTTP_200_OK)

@router.post(
    "/create",
    summary="Create a project",
    responses={
        201: {"description": "Successful response", "model": ResponseSchema[ProjectResponseSchema]},
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
    tags=["Projects"],
)
async def create_project_endpoint(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    project: CreateProjectSchema,
    db: Session = Depends(get_db),
):

    user = await get_current_user(db=db, token=token)

    project.limit = 50  # TODO: create a logic based on subscription

    created_project = create_project(db, project, user.id)
    project_response_data = create_project_response_data(created_project)

    response = ResponseSchema[ProjectResponseSchema](
        data=project_response_data,
        message="Project created successfully",
    )
    return JSONResponse(content=response.dict(), status_code=status.HTTP_201_CREATED)


@router.get(
    "/project/{project_id}",
    summary="Create a project",
    responses={
        200: {"description": "Successful response", "model": ResponseSchema[ProjectResponseSchema]},
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
    tags=["Projects"],
)
async def get_project_details(
    project_id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):

    user = await get_current_user(db=db, token=token)

    project = get_project_by_project_id(db, project_id, user.id)

    if project is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project not found")

    project_response_data = create_project_response_data(project)

    response = ResponseSchema[ProjectResponseSchema](
        data=project_response_data,
        message="Project retrieved successfully",
    )
    return JSONResponse(content=response.dict(), status_code=status.HTTP_200_OK)


@router.patch(
    "/project/{project_id}",
    summary="Update a project",
    responses={
        200: {"description": "Successful response", "model": ResponseSchema[ProjectResponseSchema]},
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
    tags=["Projects"],
)
async def update_project_endpoint(
    request: Request,
    project_id: str, 
    token: Annotated[str, Depends(oauth2_scheme)],
    project: ProjectSchema,
    db: Session = Depends(get_db),
):

    user = await get_current_user(db=db, token=token)

    existing_project = get_project_by_project_id(db, project_id, user.id)

    if existing_project is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project not found")

    updated_project = update_project_by_project_id(db, existing_project, project)
    
    project_response_data = create_project_response_data(updated_project)

    response = ResponseSchema[ProjectResponseSchema](
        data=project_response_data,
        message="Project updated successfully",
    )
    return JSONResponse(content=response.dict(), status_code=status.HTTP_200_OK)



@router.get(
    "/{project_id}/waitlist/list",
    summary="Get Waitlist",
    responses={
        200: {"description": "Successful response", "model": PaginatedResponseSchema[List[WaitlistResponse]]},
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
async def get_waitlist_ids(
        project_id: str,
        request: Request,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db),
) -> JSONResponse:

    user = await get_current_user(db=db, token=token)
    existing_project = get_project_by_project_id(db, project_id, user.id)
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("size", 10))
    skip = (page - 1) * page_size
    waitlist_cursor = project_waitlist_collection.find({"project_id": existing_project.id}).skip(skip).limit(page_size)
    total_count = project_waitlist_collection.count_documents({"project_id": existing_project.id})

    waitlist_data = []
    for waitlist_item in waitlist_cursor:
        waitlist_item['_id'] = str(waitlist_item['_id'])  # Convert ObjectId to string
        waitlist_item['date_added'] = waitlist_item['date_added'].isoformat()
        waitlist_data.append(WaitlistResponse(**waitlist_item))

    response = PaginatedResponseSchema[List[WaitlistResponse]](
        data=waitlist_data,
        message="Waitlist retrieved successfully",
        total=total_count
    )

    return JSONResponse(content=response.dict(), status_code=status.HTTP_200_OK)


@router.get(
    "/{project_uuid}/waitlist/download",
    summary="Download Waitlist",
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
async def download_waitlist_ids(
    project_uuid: str,
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    background_task : BackgroundTasks,
    redis: Redis = Depends(get_redis),
    db: Session = Depends(get_db),
) -> JSONResponse:
    
    user = await get_current_user(db=db, token=token)
    extension_type = request.query_params.get("ext_type", "csv")
    if extension_type not in EXTENSION_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid extension type")

    existing_project = get_project_by_project_id(db, project_uuid, user.id)
    waitlist_cursor = project_waitlist_collection.find({"project_id": existing_project.id})

    waitlist_data = []
    for waitlist_item in waitlist_cursor:
        waitlist_item['date_added'] = waitlist_item['date_added'].isoformat()
        waitlist_item.pop("_id")
        waitlist_item.pop("project_id")
        waitlist_data.append(WaitlistResponse(**waitlist_item))
    download_id = str(uuid4())
    
    background_task.add_task(download_waitlist, waitlist_data, extension_type, user.id, project_uuid, download_id)

    await redis.set(download_id, "processing", ex=3600)
    return JSONResponse(
        content={
            "message": "Waitlist download initiated successfully!",
            "data": {"download_id": download_id}
            },
        status_code=status.HTTP_200_OK
    )
    


@router.get(
    "/{project_uuid}/waitlist/download/{download_id}",
    summary="Download Waitlist",
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
async def download_waitlist_file(
    project_uuid: str,
    download_id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    redis: Redis = Depends(get_redis),
    db: Session = Depends(get_db),
) -> JSONResponse:
    
    user = await get_current_user(db=db, token=token)
    download_data = await redis.get(download_id)
    
    if not download_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Download ID. Retry after sometime!")
    elif download_data == "processing":
        return JSONResponse(
            content={
                "message": "Waitlist download is in progress.",
                },
            status_code=status.HTTP_202_ACCEPTED
        )

    return JSONResponse(
        content={
            "message": "Waitlist download initiated successfully!",
            "data": {"download_url": str(download_data)}
            },
        status_code=status.HTTP_200_OK
    )