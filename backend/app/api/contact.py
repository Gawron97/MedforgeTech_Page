from fastapi import Request

from application import app
from schemas.contact import ContactRequest, ContactResponse
from security import turnstile

@app.post("/api/contact", response_model=ContactResponse)
async def contact(
    payload: ContactRequest, 
    request: Request
):
    env = request.scope["env"]

    await turnstile.verify_turnstile(
        token=payload.turnstileToken,
        secret=env.TURNSTILE_SECRET,
        expected_action="contact",
    )

    return ContactResponse(success=True)