import json
from workers import fetch

from errors.exceptions import (
    TurnstileConfigurationError,
    TurnstileRejectedError,
    TurnstileUnavailableError,
)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

ERROR_TYPES = {
    "invalid-input-secret": TurnstileConfigurationError,
    "bad-request": TurnstileConfigurationError,

    "invalid-input-response": TurnstileRejectedError,
    "timeout-or-duplicate": TurnstileRejectedError,

    "internal-error": TurnstileUnavailableError
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
        raise TurnstileRejectedError("Turnstile token is missing")

    if not secret:
        raise TurnstileConfigurationError("Turnstile secret is not configured")

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
        raise TurnstileUnavailableError("Could not connect to Turnstile service") from exc

    _validate_http_status(response.status)

    try:
        return json.loads(await response.text())
    except Exception as exc:
        raise TurnstileUnavailableError("Could not parse Turnstile response") from exc

def _validate_http_status(status: int) -> None:
    if 200 <= status < 300:
        return

    if status == 429 or status >=500:
        raise TurnstileUnavailableError(f"Turnstile service returned status {status}")

    raise TurnstileConfigurationError(f"Turnstile service returned status {status}")

def _validate_result(
        result: dict,
        expected_action: str | None,
        expected_hostname: str | None
) -> None:

    if result.get("success") is not True:
        _raise_for_error_codes(result.get("error-codes", []))

    if expected_action is not None and result.get("action") != expected_action:
        raise TurnstileRejectedError(f"Turnstile action mismatch: expected {expected_action}, got {result.get('action')}")

    if expected_hostname is not None and result.get("hostname") != expected_hostname:
        raise TurnstileRejectedError(f"Turnstile hostname mismatch: expected {expected_hostname}, got {result.get('hostname')}")

def _raise_for_error_codes(error_codes: list[str]) -> None:
    for error_code in error_codes:
        error_type = ERROR_TYPES.get(error_code)

        if error_type is not None:
            raise error_type(f"Turnstile error: {error_code}")

    raise TurnstileUnavailableError(f"Turnstile returned unknown error codes: {error_codes}")