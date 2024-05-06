from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.config.settings import BASE_DIR

router = APIRouter(prefix="")
templates = Jinja2Templates(directory=str(BASE_DIR/"templates"))


@router.get("/")
async def landing_page(request: Request):

    return templates.TemplateResponse(
        request=request, name="home.html"
    )