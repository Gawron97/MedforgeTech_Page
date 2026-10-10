import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from application import app

from errors.exceptions import AppError, InvalidRequestError

logger = logging.getLogger(__name__)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):

    if exc.status_code >= 500:
        logger.error(f"{type(exc).__name__} path={request.url.path} code={exc.code} message={exc.message}, exc_info={type(exc), exc, exc.__traceback__}")
    else:
        logger.warning(f"{type(exc).__name__} path={request.url.path} code={exc.code} message={exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
        }
    )

@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    return await app_error_handler(
        request,
        InvalidRequestError("Request validation failed"),
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
