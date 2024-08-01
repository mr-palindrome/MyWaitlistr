from fastapi import APIRouter

from src.apps.waitlist.api.v1.endpoints import router as v1_router
from src.apps.waitlist.api.v2.endpoints import router as v2_router

router = APIRouter(prefix="/waitlist")

router.include_router(router=v1_router)
router.include_router(router=v2_router)
