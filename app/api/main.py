"""
FastAPI application factory.

Creates and configures the CryptoGraph API application,
including router registration and health check endpoint.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint

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
        max_body_size=10 * 1024 * 1024 + 64 * 1024,
        form_limits={"max_files": 1, "max_fields": 2, "max_part_size": 32768},
    )

    @app.middleware("http")
    async def request_safety(request: Request, call_next: RequestResponseEndpoint):
        lengths = request.headers.getlist("content-length")
        if lengths and (len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit()):
            response = JSONResponse({"detail": "Invalid Content-Length"}, status_code=400)
        else:
            response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.method == "POST":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, error: RequestValidationError):
        # Validation errors can carry the submitted text or private PEM in
        # input/ctx. Keep the useful field locations and omit request values.
        detail = [
            {field: issue[field] for field in ("type", "loc", "msg")}
            for issue in error.errors()
        ]
        return JSONResponse({"detail": detail}, status_code=422)

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
