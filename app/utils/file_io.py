"""
File I/O utilities.

Helper functions for file handling used in the CryptoGraph
application, primarily for processing uploaded files.
"""


async def read_upload(file, max_size_mb: int = 10) -> bytes:
    """
    Read the contents of an uploaded file.

    Args:
        file: A FastAPI UploadFile object.

    Returns:
        The raw bytes content of the file.
    """
    if max_size_mb <= 0:
        raise ValueError('Maximum file size must be positive')
    # Read no more than the allowed size plus one sentinel byte, so the
    # handler never materializes an unbounded payload in application memory.
    file_bytes = await file.read(max_size_mb * 1024 * 1024 + 1)
    if not validate_file_size(file_bytes, max_size_mb=max_size_mb):
        raise ValueError(f'File exceeds the {max_size_mb} MiB upload limit')
    return file_bytes


def validate_file_size(file_bytes: bytes, max_size_mb: int = 10) -> bool:
    """
    Validate that file content does not exceed the maximum size.

    Args:
        file_bytes: The raw bytes of the file.
        max_size_mb: Maximum allowed file size in megabytes (default: 10).

    Returns:
        True if the file is within the size limit, False otherwise.
    """
    max_bytes = max_size_mb * 1024 * 1024
    return len(file_bytes) <= max_bytes
