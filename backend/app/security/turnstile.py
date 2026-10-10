import json
from workers import fetch

from errors.codes import ErrorCode
from errors.exceptions import (
    AppError,
    ForbiddenError,
    InternalError,
    ServiceUnavailableError,
)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

ERROR_MAPPING: dict[str, tuple[type[AppError], ErrorCode]] = {
    "missing-input-secret": (InternalError, ErrorCode.INTERNAL_ERROR),
    "invalid-input-secret": (InternalError, ErrorCode.INTERNAL_ERROR),
    "bad-request": (InternalError, ErrorCode.INTERNAL_ERROR),

    "missing-input-response": (ForbiddenError, ErrorCode.CAPTCHA_VERIFICATION_FAILED),
    "invalid-input-response": (ForbiddenError, ErrorCode.CAPTCHA_VERIFICATION_FAILED),
    "timeout-or-duplicate": (ForbiddenError, ErrorCode.CAPTCHA_VERIFICATION_FAILED),

    "internal-error": (ServiceUnavailableError, ErrorCode.CAPTCHA_VERIFICATION_UNAVAILABLE),
}

async def verify_turnstile(
        token: str, 
        secret: str, 
        remote_ip: str | None = None, 
        expected_action: str | None = None,
        expected_hostname: str | None = None
) -> None:

    _validate_input(token, secret)

    result = await _call_turnstile(token, secret, remote_ip)

    _validate_result(result, expected_action, expected_hostname)

def _validate_input(
        token: str,
        secret: str,
) -> None:
    if not token:
        raise ForbiddenError(ErrorCode.CAPTCHA_VERIFICATION_FAILED, "Turnstile token is missing")

    if not secret:
        raise InternalError(ErrorCode.INTERNAL_ERROR, "Turnstile secret is not configured")

async def _call_turnstile(
        token: str,
        secret: str,
        remote_ip: str | None
) -> dict:

    data = {
        "secret": secret,
        "response": token,
    }

    if remote_ip:
        data["remoteip"] = remote_ip

    try:
        response = await fetch(
            TURNSTILE_VERIFY_URL,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(data)
        )
    except Exception as exc:
        raise ServiceUnavailableError(
            ErrorCode.CAPTCHA_VERIFICATION_UNAVAILABLE,
            "Could not connect to Turnstile service",
        ) from exc

    _validate_http_status(response.status)

    try:
        return json.loads(await response.text())
    except Exception as exc:
        raise ServiceUnavailableError(
            ErrorCode.CAPTCHA_VERIFICATION_UNAVAILABLE,
            "Could not parse Turnstile response",
        ) from exc

def _validate_http_status(status: int) -> None:
    if 200 <= status < 300:
        return

    if status in (408, 429) or status >=500:
        raise ServiceUnavailableError(
            ErrorCode.CAPTCHA_VERIFICATION_UNAVAILABLE,
            f"Turnstile service returned status {status}",
        )

    raise InternalError(ErrorCode.INTERNAL_ERROR, f"Turnstile service returned status {status}")

def _validate_result(
        result: dict,
        expected_action: str | None,
        expected_hostname: str | None
) -> None:

    if result.get("success") is not True:
        _raise_for_error_codes(result.get("error-codes", []))

    if expected_action is not None and result.get("action") != expected_action:
        raise ForbiddenError(
            ErrorCode.CAPTCHA_VERIFICATION_FAILED,
            f"Turnstile action mismatch: expected {expected_action}, got {result.get('action')}",
        )

    if expected_hostname is not None and result.get("hostname") != expected_hostname:
        raise ForbiddenError(
            ErrorCode.CAPTCHA_VERIFICATION_FAILED,
            f"Turnstile hostname mismatch: expected {expected_hostname}, got {result.get('hostname')}",
        )

def _raise_for_error_codes(error_codes: list[str]) -> None:
    for error_code in error_codes:
        error = ERROR_MAPPING.get(error_code)

        if error is not None:
            error_type, code = error
            raise error_type(code, f"Turnstile error: {error_code}")

    raise ServiceUnavailableError(
        ErrorCode.CAPTCHA_VERIFICATION_UNAVAILABLE,
        f"Turnstile returned unknown error codes: {error_codes}",
    )
