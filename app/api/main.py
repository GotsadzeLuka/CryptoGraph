"""
FastAPI application factory.

Creates and configures the CryptoGraph API application,
including router registration and health check endpoint.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes_classical import router as classical_router
from app.api.routes_modern import router as modern_router
from app.api.routes_files import router as files_router
from app.api.schemas import HealthResponse


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        A configured FastAPI application instance with all routers
        registered and metadata for the Swagger UI.
    """
    app = FastAPI(
        title="CryptoGraph API",
        description=(
            "A cryptography toolbox API supporting classical ciphers "
            "(Caesar, Vigenère), SHA-256 hashing, RSA encryption/decryption, "
            "and RSA digital signatures."
        ),
        version="1.0.0",
    )

    @app.middleware("http")
    async def request_safety(request: Request, call_next):
        # Enforce declared request size. A proxy must still cap chunked bodies.
        length = request.headers.get("content-length")
        if length is not None:
            try:
                if int(length) > 10 * 1024 * 1024 + 64 * 1024:
                    return JSONResponse(status_code=413, content={"detail": "Request body exceeds the upload limit"})
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.url.path.startswith("/api/modern/rsa/") or request.url.path.startswith("/api/files/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    # Register API routers
    app.include_router(classical_router)
    app.include_router(modern_router)
    app.include_router(files_router)

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check() -> HealthResponse:
        """Check if the API is running."""
        return HealthResponse()

    return app
