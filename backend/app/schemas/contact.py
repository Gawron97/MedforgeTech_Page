from pydantic import BaseModel

class ContactRequest(BaseModel):
    name: str
    email: str
    message: str
    turnstileToken: str
    language: str

class ContactResponse(BaseModel):
    success: bool