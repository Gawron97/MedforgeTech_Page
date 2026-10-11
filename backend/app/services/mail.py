import json

from workers import fetch

from errors.codes import ErrorCode
from errors.exceptions import InternalError, ServiceUnavailableError
from schemas.contact import ContactRequest

RESEND_SEND_URL = "https://api.resend.com/emails"

class MailService:
    def __init__(self, api_key: str, sender: str, recipient: str):
        if not all((api_key, sender, recipient)):
            raise InternalError(ErrorCode.INTERNAL_ERROR, "Mail service configuration is not complete")

        self._api_key = api_key
        self._sender = sender
        self._recipient = recipient

    async def send_contact_email(self, contact: ContactRequest) -> None:
        data = {
            "from": self._sender,
            "to": [self._recipient],
            "reply_to": contact.email,
            "subject": f"New contact request from {contact.name}",
            "text": (
                f"Name: {contact.name}\n"
                f"Email: {contact.email}\n"
                f"Language: {contact.language}\n"
                f"Message: {contact.message}"
            )
        }

        try:
            response = await fetch(
                RESEND_SEND_URL,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                },
                body=json.dumps(data)
            )
        except Exception as exc:
            raise ServiceUnavailableError(
                ErrorCode.EMAIL_SEND_UNAVAILABLE,
                "Could not connect to Resend API"
            ) from exc

        if 200 <= response.status < 300:
            return

        if response.status in (408, 429) or response.status >= 500:
            raise ServiceUnavailableError(
                ErrorCode.EMAIL_SEND_UNAVAILABLE,
                f"Resend API returned status code {response.status}"
            )

        raise InternalError(
            ErrorCode.INTERNAL_ERROR,
            f"Resend API returned status code {response.status} with body: {await response.text()}"
        )