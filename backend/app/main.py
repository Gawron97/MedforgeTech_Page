from fastapi import FastAPI
from workers import asgi

from application import app

import api
import errors

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

Default = asgi.entrypoint(app)