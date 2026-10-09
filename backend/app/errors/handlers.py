import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from application import app

from errors.exceptions import AppError

logger = logging.getLogger(__name__)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):

    if exc.status_code >= 500:
        logger.error(f"{type(exc).__name__} path={request.url.path} code={exc.code} message={exc.message}")
    else:
        logger.warning(f"{type(exc).__name__} path={request.url.path} code={exc.code} message={exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
        }
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):

    logger.exception(f"Unexpected error path={request.url.path}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": "INTERNAL_ERROR",
        }
    )