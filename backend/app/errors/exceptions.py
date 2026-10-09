
class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str | None = None):
        self.message = message
        super().__init__(message or self.code)

class TurnstileRejectedError(AppError):
    status_code = 403
    code = "VERIFICATION_FAILED"

class TurnstileConfigurationError(AppError):
    status_code = 500
    code = "INTERNAL_ERROR"

class TurnstileUnavailableError(AppError):
    status_code = 503
    code = "VERIFICATION_UNAVAILABLE"