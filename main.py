"""
Main FastAPI Application Entry Point

This module initializes the FastAPI server and sets up routes.
The tokenizer patch is imported first to ensure compatibility with Python 3.13.
"""

# CRITICAL: Import tokenizer patch BEFORE any livekit imports
import tokenizer_patch  # noqa: F401

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.api_debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles initialization and cleanup of resources.
    """
    # Startup
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"LiveKit URL: {settings.livekit_url}")
    
    # Verify LiveKit agents can be imported (optional on Vercel)
    # Note: livekit-agents is not included in requirements-vercel.txt to stay under 250 MB
    # Deploy backend with livekit-agents on Railway/Render and use minimal_vercel_proxy.py
    try:
        from livekit import agents
        logger.info("✓ LiveKit agents imported successfully")
    except ImportError as e:
        logger.warning(
            f"⚠ LiveKit agents not available (expected on Vercel): {e}. "
            "For voice agent functionality, deploy backend on Railway/Render with livekit-agents."
        )
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint - health check and API information.
    """
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "healthy",
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
    }


@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return {"status": "ok"}


# Import and include routers here
# Example:
# from routers import voice_agent
# app.include_router(voice_agent.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level="info" if not settings.api_debug else "debug",
    )

