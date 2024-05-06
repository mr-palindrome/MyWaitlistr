from fastapi import APIRouter, Depends, Response
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from src.apps.waitlist.router import router as waitlist_router
from src.config.settings import ENV_NAME

app_router: APIRouter = APIRouter(prefix='/api')


@app_router.get("/", include_in_schema=False)
def health_check():
    return Response(
        content="Healthy",
        status_code=200,
        headers={"content-type": "application/json"},
    )


if ENV_NAME.lower() in ["dev"]:

    @app_router.get("/docs", include_in_schema=False)
    def get_docs():
        return get_swagger_ui_html(openapi_url="openapi.json", title="SAMS API Documentation")

    @app_router.get("/redoc", include_in_schema=False)
    def get_redoc():
        return get_redoc_html(openapi_url="openapi.json", title="SAMS API Documentation")

    @app_router.get("/openapi.json", include_in_schema=False)
    def openapi():
        return get_openapi(title="SAMS API Documentation", version="0.1.0", routes=app_router.routes)

app_router.include_router(waitlist_router)