"""
Main Application - FastAPI Entrypoint

Initializes FastAPI app, configures middleware, registers routes,
and handles application lifecycle events.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import create_db_and_tables, close_db_connection
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.utils.logger import setup_logging

# Import all controllers
from app.controller.diagram_controller import router as diagram_router
from app.controller.user_preference_controller import router as preference_router
from app.controller.health_controller import router as health_router

# Setup logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info("=" * 60)
    logger.info("Starting DiagramGPT FastAPI Application")
    logger.info("=" * 60)
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")  # Don't log credentials
    logger.info(f"OpenAI Model: {settings.OPENAI_MODEL}")
    logger.info(f"Cache Enabled: {settings.ENABLE_CACHE}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    
    # Initialize database
    try:
        await create_db_and_tables()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise
    
    logger.info("=" * 60)
    logger.info("Application started successfully")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down DiagramGPT...")
    await close_db_connection()
    logger.info("✓ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="DiagramGPT",
    description="Generate diagrams from natural language using LLM and Graphviz",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Add middleware (order matters - last added is executed first)

# 1. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request ID middleware (for tracking)
app.add_middleware(RequestIDMiddleware)

# 3. Error handler middleware (catches all exceptions)
app.add_middleware(ErrorHandlerMiddleware)


# Register routers

# Health check routes (no prefix)
app.include_router(health_router)

# API routes
app.include_router(diagram_router)
app.include_router(preference_router)


# Mount static files (frontend) - MUST be after API routes
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
    logger.info("✓ Frontend static files mounted at /")
except RuntimeError:
    logger.warning("⚠ Frontend directory not found. Static files will not be served.")


# Root endpoint (if static files not mounted)
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": "DiagramGPT API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
