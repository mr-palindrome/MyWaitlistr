from fastapi import FastAPI

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


app = FastAPI(
    title="MyWaitlistr",
    openapi_tags=[
        {"name": "Base", "description": "Operations related to base"},
        {"name": "Waitlist", "description": "Operations related to waitlists"},
    ]
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
