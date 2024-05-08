import sentry_sdk

from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import app
from src.apps.app_router import app_router
from src.apps.base.exception_handler import http_custom_exception_handler
from src.config.logs.sentry_management.sentry_manager import initialize_sentry


initialize_sentry()

app.add_exception_handler(HTTPException, http_custom_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
