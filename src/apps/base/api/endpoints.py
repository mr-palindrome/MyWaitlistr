from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.config.settings import BASE_DIR, templates

router = APIRouter(prefix="")


@router.get("/", tags=["Base"])
async def landing_page(request: Request):

    return templates.TemplateResponse(request=request, name="home.html")
