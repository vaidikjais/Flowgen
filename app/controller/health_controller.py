"""
Health Controller - API Endpoints for Health Checks

Provides health check and status endpoints for monitoring.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session, check_db_connection
from app.core.config import settings
from app.schemas.common_schema import HealthResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Simple health check endpoint.
    
    Returns basic status and version information.
    """
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )


@router.get("/api/health", response_model=HealthResponse)
async def detailed_health_check(db: AsyncSession = Depends(get_session)):
    """
    Detailed health check endpoint.
    
    Checks:
    - Database connection
    - LLM API availability (via config)
    
    Returns detailed status for each component.
    """
    # Check database connection
    db_status = "ok" if await check_db_connection() else "error"
    
    # Check LLM availability (just checks if API key is configured)
    llm_status = "ok" if settings.OPENAI_API_KEY else "not_configured"
    
    overall_status = "ok" if db_status == "ok" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        database=db_status,
        llm=llm_status
    )

