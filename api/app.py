from fastapi import FastAPI
from api.kb_api import router

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION
)

app.include_router(router)