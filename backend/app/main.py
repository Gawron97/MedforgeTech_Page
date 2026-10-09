from fastapi import FastAPI
from workers import asgi

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI()
Default = asgi.entrypoint(app)