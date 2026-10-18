"""
Image Validation and Processing Utilities for FastAPI endpoints.
Validates MIME types, byte length, dimensions, and PIL decoding integrity.
"""
import io
from typing import Tuple, Set
from fastapi import UploadFile, HTTPException, status
from PIL import Image

ALLOWED_MIME_TYPES: Set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "application/octet-stream"  # sometimes sent by clients; validated via PIL
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_IMAGE_DIMENSION = 50

async def validate_and_load_image(file: UploadFile) -> Image.Image:
    """
    Validates uploaded file MIME type, size, and image integrity.
    Returns RGB PIL Image.
    """
    # 1. MIME type header check
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Please upload JPEG, PNG, or WebP images."
        )

    # 2. Read bytes
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image file exceeds maximum allowable size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
        )

    # 3. Decode with PIL to ensure no corrupted/truncated image payload
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # Verifies file structure
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupted or invalid image data: {str(e)}"
        )

    # 4. Re-open to read pixels and check dimensions
    try:
        image = Image.open(io.BytesIO(contents))
        w, h = image.size
        if w < MIN_IMAGE_DIMENSION or h < MIN_IMAGE_DIMENSION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image resolution too low ({w}x{h}). Minimum required dimension is {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}."
            )
        return image.convert("RGB")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process image: {str(e)}"
        )
