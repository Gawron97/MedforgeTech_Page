from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal

class ContactRequest(BaseModel):

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=254)
    message: str = Field(min_length=1, max_length=5000)
    turnstileToken: str = Field(min_length=1, max_length=2048)
    language: Literal["pl", "en"]

class ContactResponse(BaseModel):
    success: bool