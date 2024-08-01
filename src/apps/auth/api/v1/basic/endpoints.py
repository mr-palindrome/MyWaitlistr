from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated

from src.config.db.postgres_management.pg_manager import get_db, engine
from src.apps.auth.service import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_password,
    verify_user,
    get_current_user,
)
from src.apps.auth.schemas.user_schema import (
    CeateUserSchema,
    UserResponseSchema,
    UserDetailsSchema,
    LoginUserSchema,
    RefreshTokenSchema,
    ChangePasswordSchema,
)
from src.apps.base.schemas.reponse_types import (
    ResponseSchema,
    SuccessResponse,
    BadGatewayResponse,
    BadRequestResponse,
    InternalServerErrorResponse,
    # NotAuthorizedReponse,
    ServiceUnavailableResponse,
    TooManyRequestsReponse,
)
from src.apps.auth.models import User, Token
from src.apps.auth.utils.auth import create_access_token, create_refresh_token
from src.apps.auth.utils.password import oauth2_scheme, verify_pwd, secure_pwd

User.__table__.create(bind=engine, checkfirst=True)
Token.__table__.create(bind=engine, checkfirst=True)

router = APIRouter(prefix="/v1")


@router.post(
    "/register",
    summary="Register a new user",
    responses={
        200: {"description": "Successful response", "model": UserResponseSchema},
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
    tags=["Auth"],
)
async def register_user(
    request: Request, payload: CeateUserSchema, db: Session = Depends(get_db)
) -> JSONResponse:

    if not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please add Email",
        )
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {payload.email} already exists",
        )
    elif get_user_by_username(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username {payload.username} already exists",
        )
    if not payload.username:
        payload.username = payload.email

    user = create_user(db=db, user=payload)

    if not user:
        raise HTTPException(status_code=502, detail="Bad Gateway")

    access_token = create_access_token(data={"sub": user.username, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return JSONResponse(
        status_code=200,
        content={
            "message": "User created successfully!",
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        },
    )


@router.post(
    "/login",
    summary="Login a user",
    responses={
        200: {"description": "Successful response", "model": UserResponseSchema},
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
    tags=["Auth"],
)
async def login_user(
    request: Request, payload: LoginUserSchema, db: Session = Depends(get_db)
) -> JSONResponse:

    user = verify_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check your email and password and try again.",
        )

    access_token = create_access_token(data={"sub": user.username, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return JSONResponse(
        status_code=200,
        content={
            "message": "User logged in successfully!",
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        },
    )


@router.post(
    "/refresh",
    summary="Refresh token",
    responses={
        200: {"description": "Successful response", "model": UserResponseSchema},
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
    tags=["Auth"],
)
async def refresh_token(
    request: Request,
    # token: Annotated[str, Depends(oauth2_scheme)],
    payload: RefreshTokenSchema,
    db: Session = Depends(get_db),
) -> JSONResponse:

    current_user = await get_current_user(db=db, token=payload.refresh)

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    access_token = create_access_token(data={"sub": current_user.username, "email": current_user.email})
    refresh_token = create_refresh_token(data={"sub": current_user.username})

    return JSONResponse(
        status_code=200,
        content={
            "message": "Token refreshed successfully!",
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        },
    )


@router.post(
    "/change-password",
    summary="Change password",
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
    tags=["Auth"],
)
async def change_password(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    payload: ChangePasswordSchema,
    db: Session = Depends(get_db),
) -> JSONResponse:

    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    user = await get_current_user(db=db, token=token)

    if not verify_pwd(payload.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check your old password and try again.",
        )

    user = update_password(db, user, payload.new_password)

    return JSONResponse(
        status_code=200,
        content={"message": "Password changed successfully!"},
    )


@router.get(
    "/user",
    summary="Get user details",
    responses={
        200: {"description": "Successful response", "model": ResponseSchema[UserDetailsSchema]},
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
    tags=["Auth"],
)
async def get_user_details(
    request: Request, 
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_db)
) -> JSONResponse:

    user = await get_current_user(db=db, token=token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    user_data = UserDetailsSchema.from_orm(user).dict()

    response = ResponseSchema[UserDetailsSchema](
        message="User details retrieved successfully!",
        data=user_data
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.dict(),
    )