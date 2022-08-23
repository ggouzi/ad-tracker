# FastAPI imports
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_redoc_html
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler

import datetime
import settings
import uvicorn
import logging

from crud import user_crud, post_crud, media_crud
from instagram_api_wrapper import user_wrapper, post_wrapper
from schemas import media_schema
from db.database import get_db
from api import posts_routes, users_routes
from cron import scheduler_cron
import launch

from starlette.responses import JSONResponse
from logging.handlers import RotatingFileHandler
from exceptions.CustomException import CustomException

# LOGGING_FILE = "logs/system.log"
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         RotatingFileHandler(LOGGING_FILE, maxBytes=200000, backupCount=100)
#     ]
# )

# logger = logging.getLogger()
# print = logger.info


# HTTP Handlers

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

@app.exception_handler(CustomException)
async def radis_exception_handler(request: Request, exception: CustomException):
    ex = HTTPException(
        status_code=exception.status_code,
        detail=exception.detail
    )
    logging.error(exception.info)
    return await http_exception_handler(request, ex)

INSTAGRAM_API = launch.connect()
app.include_router(posts_routes.router)
app.include_router(users_routes.router)
scheduler_cron.sched.start()


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=settings.env.port)
