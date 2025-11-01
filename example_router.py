"""
Example Router Module

This is an example router showing how to use LiveKit agents in your FastAPI routes.
You can use this as a template or delete it if not needed.

To use this router, uncomment the import in main.py:
    from example_router import router as example_router
    app.include_router(example_router, prefix="/api/v1")
"""

# CRITICAL: Ensure tokenizer patch is imported first (handled in main.py)
# Import tokenizer_patch before any livekit imports

from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/example", tags=["example"])


@router.get("/test-livekit")
async def test_livekit_import():
    """
    Test endpoint to verify LiveKit agents can be imported successfully.
    This endpoint demonstrates that the tokenizer patch is working.
    """
    try:
        # This import should work now thanks to tokenizer_patch.py
        from livekit import agents
        
        return {
            "status": "success",
            "message": "LiveKit agents imported successfully",
            "patch_applied": True,
        }
    except ImportError as e:
        logger.error(f"Failed to import LiveKit agents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"LiveKit agents import failed: {str(e)}",
        )


@router.get("/info")
async def get_agent_info():
    """
    Example endpoint that could fetch agent information.
    This is a placeholder for actual agent functionality.
    """
    return {
        "message": "Voice agent endpoint",
        "status": "operational",
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro}",
    }

