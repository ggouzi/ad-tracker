# FastAPI imports
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_redoc_html

import settings
import uvicorn
import logging

from api import keywords_routes, medias_routes, posts_routes, users_routes
from cron import scheduler_cron

from starlette.responses import JSONResponse
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CustomException)
async def radis_exception_handler(request: Request, exception: CustomException):
    ex = HTTPException(
        status_code=exception.status_code,
        detail=exception.detail
    )
    logging.error(exception.info)
    return await http_exception_handler(request, ex)


# Docs
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    # db_user = user_crud.check_authentication(db, email=credentials.username, password=credentials.password)
    # if not db_user:
    #     raise CustomException(db=db, status_code=401, detail='bad_username_password', info=f'Cannot find activated User with email {credentials.username} and specified password', language='fr-FR')

    openapi_schema = get_openapi(
        title="Instagram Ad Tracker Documentation API",
        version="0.1",
        routes=app.routes,
        description="Postman Collection: https://www.getpostman.com/collections/d70cb199822c476eb4b0",
        openapi_version="3.0.2",
    )

    openapi_schema["info"]["x-logo"] = {
        "url": f"https://media{settings.env.env}.leradis.io/radis.jpeg"
    }
    app.openapi_schema = openapi_schema
    return JSONResponse(openapi_schema)


@app.get("/docs", include_in_schema=False)
async def get_documentation():
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


@app.get("/", include_in_schema=False)
async def redirect():
    response = RedirectResponse(url='/radis/docs')
    return response


app.include_router(keywords_routes.router)
app.include_router(medias_routes.router)
app.include_router(posts_routes.router)
app.include_router(users_routes.router)
scheduler_cron.sched.start()

# Mount static files for terms & conditions and privacy statements
app.mount("/", StaticFiles(directory="static/"))


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=settings.env.port)
