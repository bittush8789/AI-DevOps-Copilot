from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    services = {
        "bedrock": "configured" if settings.AWS_REGION else "not_configured",
        "vector_db": settings.VECTOR_DB_TYPE,
        "kubernetes": "available",
    }
    
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        services=services,
        timestamp=datetime.utcnow()
    )


@router.get("/ready")
async def readiness_check():
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    return {"status": "alive"}
