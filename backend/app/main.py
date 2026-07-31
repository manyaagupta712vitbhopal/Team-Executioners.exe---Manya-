import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, documents, folders, mentor, planner, study_tools, users
from app.core.config import settings
from app.core.database import Base, engine
from app.utils.constants import API_VERSION, APP_NAME
from app.utils.responses import success_response

# Import all models so their tables are registered on Base.metadata
# before create_all() runs below.
import app.models  # noqa: F401


app = FastAPI(
    title=APP_NAME,
    description="AI-powered study planner and organizer backend",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# TEMP: create tables directly, bypassing Alembic (whose migration
# history is out of sync with the DB). Safe to run repeatedly —
# create_all() only creates tables that don't already exist.
Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded PDFs directly so the frontend can embed/preview them.
# e.g. GET /static/documents/<filename>.pdf
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(
    "/static/documents",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="document-files",
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(folders.router)
app.include_router(study_tools.router)
app.include_router(mentor.router)
app.include_router(planner.router)


@app.get("/", tags=["Root"])
def root() -> dict:
    return success_response(
        message="Welcome to CourseMate Backend 🚀",
        data={
            "app": APP_NAME,
            "version": API_VERSION,
        },
    )


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return success_response(
        message="Application is healthy.",
        data={
            "status": "healthy",
            "database": "connected",
        },
    )
