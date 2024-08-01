from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def http_custom_exception_handler(request: Request, exc: HTTPException):

    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
