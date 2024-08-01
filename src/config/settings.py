import os
import pytz
from pathlib import Path

from decouple import config

from fastapi.templating import Jinja2Templates
from src.apps.base.s3_helpers import get_s3_object


local_timezone = pytz.timezone("Asia/Kolkata")

ENV_NAME = config("ENV_NAME")

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
BUCKET_NAME = config("BUCKET_NAME")


ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"

MONGO_DB_URI = config("MONGO_DB_URI")
MONGO_DB_NAME = config("MONGO_DB_NAME")

# POSTGRES_DB_URI = config("POSTGRES_DB_URI")

DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_NAME = config("DB_NAME")

SENTRY_DSN = config("SENTRY_DSN")

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


GOOGLE_FILE_NAME = "google_secrets_local.json"

BASE_FRONTEND_URL = config("BASE_FRONTEND_URL")
GOOGLE_SECRET_FILE = get_s3_object(BUCKET_NAME, f'config/{GOOGLE_FILE_NAME}').get(
    "web", {}
)
GOOGLE_OAUTH2_CLIENT_ID = GOOGLE_SECRET_FILE.get("client_id")
GOOGLE_OAUTH2_CLIENT_SECRET = GOOGLE_SECRET_FILE.get("client_secret")
GOOGLE_REDIRECT_URI = GOOGLE_SECRET_FILE.get("redirect_uris")[0]
