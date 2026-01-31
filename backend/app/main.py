from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, matches, clips, health

app = FastAPI(
    title="SK8 API",
    description="The realest SKATE game. One take. No edits. Pure skill.",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "app": "SK8",
        "version": "1.0.0",
        "status": "running",
        "message": "One take. No edits. No excuses.",
        "docs": "/api/docs" if settings.DEBUG else None
    }

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(matches.router, prefix="/api/v1/matches", tags=["matches"])
app.include_router(clips.router, prefix="/api/v1/clips", tags=["clips"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
