"""
Minimal Vercel Proxy Example

Use this if you need a lightweight Vercel deployment that proxies to a backend.
This keeps Vercel deployment small while routing to a larger backend service.

Replace the backend URL with your actual backend (Railway, Render, etc.)
"""

from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import os

app = FastAPI(title="Voice Agent Proxy")

# Backend URL - set this in Vercel environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "https://your-backend.railway.app")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Voice Agent Proxy",
        "backend": BACKEND_URL,
        "status": "healthy"
    }


@app.get("/health")
async def health():
    """Health check for monitoring."""
    return {"status": "ok"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """
    Proxy all requests to the backend service.
    Preserves query parameters, headers, and request body.
    """
    url = f"{BACKEND_URL}/{path}"
    
    # Get query parameters
    params = dict(request.query_params)
    
    # Get request body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Forward headers (optional: filter sensitive headers)
    headers = dict(request.headers)
    # Remove host header to use backend's host
    headers.pop("host", None)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                params=params,
                content=body,
                headers=headers,
            )
            
            # Return response with same status and headers
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type", "application/json"),
            )
        except httpx.RequestError as e:
            return Response(
                content=f'{{"error": "Backend connection failed: {str(e)}"}}',
                status_code=502,
                media_type="application/json",
            )

