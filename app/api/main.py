"""
FastAPI application factory.

Creates and configures the CryptoGraph API application,
including router registration and health check endpoint.
"""

from fastapi import FastAPI, Request

from app.api.body_limit import MaxRequestBodyMiddleware

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
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.url.path.startswith("/api/modern/rsa/") or request.url.path.startswith("/api/files/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    # The last middleware registered runs outermost, before form parsing.
    # This counts actual received bytes including streaming/chunked requests.
    app.add_middleware(MaxRequestBodyMiddleware, max_bytes=10 * 1024 * 1024 + 64 * 1024)

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
