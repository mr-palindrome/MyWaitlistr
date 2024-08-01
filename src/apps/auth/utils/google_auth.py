import requests
from typing import Dict, Any
from src.config import settings
from fastapi.exceptions import ValidationException
from src.apps.auth.utils.auth import create_access_token, create_refresh_token


GOOGLE_ID_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    access_token = create_access_token(data={"sub": user.username, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return access_token, refresh_token


def google_get_access_token(*, code: str, redirect_uri: str) -> str:
    data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    import json

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

    if not response.ok:
        raise ValidationException("Failed to obtain access token from Google.")

    access_token = response.json()["access_token"]

    return access_token


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(GOOGLE_USER_INFO_URL, params={"access_token": access_token})

    if not response.ok:
        raise ValidationException("Failed to obtain user info from Google.")

    return response.json()
