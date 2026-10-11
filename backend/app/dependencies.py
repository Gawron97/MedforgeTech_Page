from typing import Any, TypeVar
from fastapi import Request

from security.turnstile import TurnstileVerifier
from services.mail import MailService

T = TypeVar("T")

_instances: dict[
    type[Any],
    tuple[tuple[Any, ...], dict[str, Any], Any],
] = {}

def get_cached_instance(
    cls: type[T],
    *args: Any,
    **kwargs: Any
) -> T:
    cached = _instances.get(cls)

    if cached is not None:
        previous_args, previous_kwargs, instance = cached
        if previous_args == args and previous_kwargs == kwargs:
            return instance

    instance = cls(*args, **kwargs)
    _instances[cls] = (args, kwargs, instance)

    return instance

async def get_turnstile_verifier(request: Request) -> TurnstileVerifier:
    env = request.scope["env"]
    return get_cached_instance(
        TurnstileVerifier,
        secret=env.TURNSTILE_SECRET,
        expected_hostname=env.TURNSTILE_HOSTNAME,
    )

async def get_mail_service(request: Request) -> MailService:
    env = request.scope["env"]
    return get_cached_instance(
        MailService,
        api_key=env.RESEND_API_KEY,
        sender=env.MAIL_FROM,
        recipient=env.MAIL_TO,
    )