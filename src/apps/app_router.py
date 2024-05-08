from fastapi import APIRouter, HTTPException, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, HTMLResponse

from app import app
from src.apps.waitlist.router import router as waitlist_router
from src.apps.base.router import router as base_router
from src.config.settings import ENV_NAME, BASE_DIR, templates

app_router: APIRouter = APIRouter(prefix='')


@app_router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(f"{BASE_DIR.parent}/static/favicon.ico")


@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request, name="404.html", status_code=404
        )
        # return HTMLResponse(content="<h1>404 - Not Found</h1>", status_code=404)
    # Re-raise the exception for other HTTP error codes
    raise exc
    

if ENV_NAME.lower() in ["dev"]:

    @app_router.get("/docs", include_in_schema=False)
    async def get_docs():
        return get_swagger_ui_html(openapi_url="openapi.json", title="SAMS API Documentation")

    @app_router.get("/redoc", include_in_schema=False)
    async def get_redoc():
        return get_redoc_html(openapi_url="openapi.json", title="SAMS API Documentation")

    @app_router.get("/openapi.json", include_in_schema=False)
    async def openapi():
        return get_openapi(title="SAMS API Documentation", version="0.1.0", routes=app_router.routes)

app_router.include_router(base_router)
app_router.include_router(waitlist_router)