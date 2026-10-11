from fastapi import Request, Depends
from typing import Annotated

from application import app
from dependencies import get_turnstile_verifier, get_mail_service
from schemas.contact import ContactRequest, ContactResponse
from security.turnstile import TurnstileVerifier
from services.mail import MailService

@app.post("/api/contact", response_model=ContactResponse)
async def contact(
    payload: ContactRequest, 
    request: Request,
    turnstile: Annotated[TurnstileVerifier, Depends(get_turnstile_verifier)],
    mail_service: Annotated[MailService, Depends(get_mail_service)]
):

    await turnstile.verify(
        token=payload.turnstileToken,
        remote_ip=request.headers.get("CF-Connecting-IP"),
        expected_action="contact",
    )

    await mail_service.send_contact_email(payload)

    return ContactResponse(success=True)