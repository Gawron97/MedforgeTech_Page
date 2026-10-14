import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from application import app

from errors.codes import ErrorCode
from errors.exceptions import AppError, InvalidRequestError

logger = logging.getLogger(__name__)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):

    if exc.status_code >= 500:
        logger.error(
            "%s path=%s code=%s message=%s",
            type(exc).__name__, request.url.path, exc.code.value, exc.message,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
    else:
        logger.warning(
            "%s path=%s code=%s message=%s",
            type(exc).__name__, request.url.path, exc.code.value, exc.message,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code.value,
        }
    )

@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    return await app_error_handler(
        request,
        InvalidRequestError(ErrorCode.INVALID_REQUEST, "Request validation failed"),
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):

    logger.exception(
        "Unexpected error path=%s",
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": ErrorCode.INTERNAL_ERROR.value,
        }
    )
