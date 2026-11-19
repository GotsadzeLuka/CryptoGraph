"""
File upload API routes.

Provides POST endpoints for file-based operations:
SHA-256 file hashing and RSA file signing/verification.
Files are processed in memory with a 10 MiB per-request upload cap and are not stored by the application.
"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.schemas import CryptoResponse, VerifyResponse
from app.modern import hashing, signatures
from app.utils.file_io import read_upload

router = APIRouter(prefix="/api/files", tags=["File Operations"])


@router.post("/hash", response_model=CryptoResponse)
async def hash_file(file: UploadFile = File(...)) -> CryptoResponse:
    """
    Hash an uploaded file using SHA-256.

    Accepts a file via multipart upload and returns its SHA-256 digest.
    The file is processed in memory and not stored on the server.
    """
    try:
        file_bytes = await read_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    result = hashing.hash_file(file_bytes)

    return CryptoResponse(
        algorithm="SHA-256",
        operation="hash-file",
        input=file.filename or "uploaded_file",
        result=result,
    )


@router.post("/sign", response_model=CryptoResponse)
async def sign_file(
    file: UploadFile = File(...),
    private_key: str = Form(..., description="RSA private key in PEM format"),
) -> CryptoResponse:
    """
    Sign an uploaded file using RSA digital signature.

    Accepts a file and a private key, returns the base64-encoded signature.
    """
    try:
        file_bytes = await read_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    try:
        result = signatures.sign_data(file_bytes, private_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CryptoResponse(
        algorithm="RSA-PSS",
        operation="sign-file",
        input=file.filename or "uploaded_file",
        result=result,
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_file(
    file: UploadFile = File(...),
    signature: str = Form(..., description="Base64-encoded signature"),
    public_key: str = Form(..., description="RSA public key in PEM format"),
) -> VerifyResponse:
    """
    Verify an RSA signature against an uploaded file.

    Accepts a file, signature, and public key. Returns whether
    the signature is valid.
    """
    try:
        file_bytes = await read_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    try:
        valid = signatures.verify_signature(file_bytes, signature, public_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return VerifyResponse(
        valid=valid,
        message="Signature is valid" if valid else "Signature is invalid",
    )
