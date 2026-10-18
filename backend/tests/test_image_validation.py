"""
Tests for Image Validation Utilities.
Verifies rejection of unsupported MIME types, corrupted image bytes, and undersized images.
"""
import io
import asyncio
import pytest
from PIL import Image
from fastapi import UploadFile, HTTPException
from backend.app.utils.image_utils import validate_and_load_image

def test_valid_image_upload():
    # Create valid 100x100 JPEG in memory
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color="orange")
    img.save(buf, format="JPEG")
    buf.seek(0)

    upload_file = UploadFile(filename="food.jpg", file=buf, headers={"content-type": "image/jpeg"})
    loaded_img = asyncio.run(validate_and_load_image(upload_file))

    assert loaded_img is not None
    assert loaded_img.size == (100, 100)
    assert loaded_img.mode == "RGB"

def test_corrupted_image_bytes():
    # Corrupt arbitrary byte stream
    buf = io.BytesIO(b"not_a_real_image_payload_header")
    upload_file = UploadFile(filename="corrupt.jpg", file=buf, headers={"content-type": "image/jpeg"})

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(validate_and_load_image(upload_file))
    assert exc_info.value.status_code == 400
    assert "corrupted" in exc_info.value.detail.lower() or "invalid" in exc_info.value.detail.lower()

def test_unsupported_mime_type():
    buf = io.BytesIO(b"text file content")
    upload_file = UploadFile(filename="notes.txt", file=buf, headers={"content-type": "text/plain"})

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(validate_and_load_image(upload_file))
    assert exc_info.value.status_code == 415

def test_image_dimensions_too_small():
    # 20x20 image is smaller than the 50x50 minimum threshold
    buf = io.BytesIO()
    img = Image.new("RGB", (20, 20), color="red")
    img.save(buf, format="PNG")
    buf.seek(0)

    upload_file = UploadFile(filename="tiny.png", file=buf, headers={"content-type": "image/png"})
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(validate_and_load_image(upload_file))
    assert exc_info.value.status_code == 400
    assert "too low" in exc_info.value.detail.lower()
