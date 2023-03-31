from base64 import b64decode
import json
import logging
import sys
from typing import Dict

from fastapi import (
    FastAPI,
    Response
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.status import (
    HTTP_400_BAD_REQUEST,
)

LOG_LEVEL = logging.getLevelName("INFO")


app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="JnJ Simulator Worker",
        description="API",
        version="1.0.0",
        routes=app.routes,
    )
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if openapi_schema["paths"][path][method]["responses"].get("422"):
                openapi_schema["paths"][path][method]["responses"][
                    "400"
                ] = openapi_schema["paths"][path][method]["responses"]["422"]
                openapi_schema["paths"][path][method]["responses"].pop("422")
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# configure loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "serialize": False,
                "level": LOG_LEVEL,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
                " | <level>{level: <8}</level> | <cyan>{name}</cyan>:"
                "<cyan>{function}</cyan> - <level>{message}</level>",
            }
        ]
    )


setup_logging()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Overrides FastAPI default status code for validation errors
    from 422 to 400."""
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.post("/")
def work(
    payload: Dict
):
    logging.info("message received on start")
    logging.info(f"start message {json.dumps(payload)}")

    message = payload.get('message')
    data = message.get('data')
    data = b64decode(data).decode("utf-8")
    obj = json.loads(data)

    return JSONResponse(obj, 201)

    # return Response("OK", 200)

    # return Response("Bad Request: Error At processing message", 400)
