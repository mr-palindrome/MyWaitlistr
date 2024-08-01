from fastapi import APIRouter

from src.apps.auth.api.v1.basic.endpoints import router as v1_router
from src.apps.auth.api.v1.google.endpoints import router as v1_google_router

router = APIRouter(prefix="/auth")

router.include_router(router=v1_router)
router.include_router(router=v1_google_router)
