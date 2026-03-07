from os import getenv
from fastapi import FastAPI
from core.config import settings
from core.startup import init_db
from app.api import api_router
from starlette.middleware.cors import CORSMiddleware

FRONTEND_ORIGINS = getenv("FRONTEND_ORIGINS", "").split(",")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _startup_event():
        init_db()

    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app