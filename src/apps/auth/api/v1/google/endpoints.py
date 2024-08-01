from src.apps.auth.utils.google_auth import google_get_access_token, google_get_user_info
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from src.config.db.postgres_management.pg_manager import get_db, engine
from src.apps.auth.models import User
from src.apps.auth.schemas.google_schema import GoogleInputSchema
from src.apps.auth.service import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_password,
    verify_user,
    get_current_user,
    generate_random_password
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
from src.apps.auth.utils.auth import create_access_token, create_refresh_token
from src.apps.auth.utils.password import oauth2_scheme, verify_pwd, secure_pwd

router = APIRouter(prefix="/google/v1")



@router.get(
    "/login",
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
async def google_login(
    request: Request,
    # query_params: GoogleInputSchema = Depends(),  # Validate query parameters
    db: Session = Depends(get_db),
):
    # Access validated query parameters
    query_params = request.query_params
    print(query_params)

    # Example: Get specific query parameter
    code = query_params.get('code')
    error = query_params.get('error')

    print(f"Code: {code}")
    print(f"Error: {error}")

    if error:
        return JSONResponse(
            status_code=400,
            content={"message": "Failed to login"}
        )
    
    google_access_token = google_get_access_token(code=code, redirect_uri="http://localhost:5173/google")
    user_info = google_get_user_info(access_token=google_access_token)

    print(user_info)

    user = get_user_by_email(db, user_info.get("email"))

    if not user:

        # {'sub': '116029723110942373778', 'name': 'Nayan Das', 'given_name': 'Nayan', 'family_name': 'Das', 'picture': 'https://lh3.googleusercontent.com/a/ACg8ocKSCWD_F9b6OdkS_Pfdo-hnV6hIGsdLWqsufuoHIPuPCA1z64Y5=s96-c', 'email': 'ndas5144@gmail.com', 'email_verified': True}
        user = CeateUserSchema(
            email=user_info.get("email"),
            username=user_info.get("email"),
            full_name=user_info.get("name", " "),
            password=generate_random_password(length=12),
            img_url=user_info.get("picture"),
        )

        user = create_user(db=db, user=user)

        if not user:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Bad Gateway")

    access_token = create_access_token(data={"sub": user.username, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "User created successfully!",
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        },
    )