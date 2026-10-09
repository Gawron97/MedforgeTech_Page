import json
from urllib.parse import urlencode
from workers import fetch

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

async def verify_turnstile(token: str, secret: str, remote_ip: str | None = None, expected_action: str | None = None) -> bool:

    data = {
        "secret": secret,
        "response": token,
    }
    if remote_ip:
        data["remoteip"] = remote_ip

    response = await fetch(
        TURNSTILE_VERIFY_URL,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body=urlencode(data)
    )

    results = json.loads(await response.text())

    if results.get("success") is not True:
        return False

    if expected_action is not None and results.get("action") != expected_action:
        return False

    return True