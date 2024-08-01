from fastapi import HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.apps.app_router import app_router
from src.apps.base.exception_handler import http_custom_exception_handler
from src.config.logs.sentry_management.sentry_manager import initialize_sentry

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


app = FastAPI(
    title="MyWaitlistr",
    openapi_tags=[
        {"name": "Base", "description": "Operations related to base"},
        {"name": "Waitlist", "description": "Operations related to waitlists"},
    ],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# initialize_sentry()

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
