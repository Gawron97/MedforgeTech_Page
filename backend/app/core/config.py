import os

class Settings:
    turnstile_sectet = os.environ["TURNSTILE_SECRET"]

settings = Settings()