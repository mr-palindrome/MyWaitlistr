from fastapi import APIRouter

from src.apps.projects.api.v1.endpoints import router as v1_router

router = APIRouter(prefix="/projects")

router.include_router(router=v1_router)