#!/bin/bash

echo "Polishing SK8 backend..."

# Create health endpoint
cat > app/api/v1/health.py << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime
import sys

from app.api.deps import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check"""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    try:
        await db.execute(text("SELECT 1"))
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["checks"]["database"] = f"error: {str(e)}"
        health["status"] = "unhealthy"
    
    if settings.AWS_ACCESS_KEY_ID and settings.S3_BUCKET_NAME:
        health["checks"]["s3_configured"] = "ok"
    else:
        health["checks"]["s3_configured"] = "missing"
    
    health["checks"]["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    return health
EOF

echo "✅ Created health endpoint"

# Update v1 __init__
cat > app/api/v1/__init__.py << 'EOF'
from app.api.v1 import auth, matches, clips, health
EOF

echo "✅ Updated v1 __init__"

# Update main.py
cat > app/main.py << 'EOF'
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
EOF

echo "✅ Updated main.py with health routes"

echo ""
echo "🎉 Backend polish complete!"
echo "Server should auto-reload. Test with:"
echo "  curl http://localhost:8000/api/v1/health"
