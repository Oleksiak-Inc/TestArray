from os import getenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.config import settings
from core.startup import init_db
from app.api import api_router
from starlette.middleware.cors import CORSMiddleware

FRONTEND_ORIGINS = getenv("FRONTEND_ORIGINS", "").split(",")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    yield
    # Shutdown logic (if any) would go here

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,                     # ✅ modern approach
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app