from fastapi import APIRouter

from src.apps.base.api.endpoints import router as v1_router

router = APIRouter(prefix="")

router.include_router(router=v1_router)
