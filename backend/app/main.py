from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="SK8 API",
    description="The realest SKATE game. One take. No edits. Pure skill.",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# CORS
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
        "message": "One take. No edits. No excuses."
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
