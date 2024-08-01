from fastapi import APIRouter

from src.apps.api_key.api.v1.endpoints import router as v1_router

router = APIRouter(prefix="/api_key")

router.include_router(router=v1_router)