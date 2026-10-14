from errors.codes import ErrorCode


class AppError(Exception):
    status_code = 500

    def __init__(self, code: ErrorCode, message: str | None = None):
        self.code = code
        self.message = message or code.value
        super().__init__(self.message)


class InvalidRequestError(AppError):
    status_code = 422


class ForbiddenError(AppError):
    status_code = 403


class ServiceUnavailableError(AppError):
    status_code = 503


class InternalError(AppError):
    status_code = 500
