import hashlib
import mimetypes
import os
import re
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings
from app.core.errors import SentinelError


MAX_UPLOAD_SIZE = settings.MAX_UPLOAD_SIZE
ALLOWED_EVIDENCE_TYPES = {
    "message/rfc822",
    "text/plain",
    "application/octet-stream",
}


def sanitize_filename(filename: str | None) -> str:
    """Strip path traversal and dangerous characters from an uploaded filename."""
    if not filename:
        return f"unnamed-{uuid4().hex}"

    # Take basename only; reject path separators and parent references.
    name = Path(filename).name
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        return f"unnamed-{uuid4().hex}"

    # Remove control characters and shell metacharacters.
    name = re.sub(r"[\x00-\x1f\x7f]", "", name)
    name = re.sub(r"[<>:\"|?*]", "_", name)

    if not name:
        return f"unnamed-{uuid4().hex}"

    return name


def validate_upload(file: UploadFile) -> None:
    """Validate size and content type before reading the file."""
    # FastAPI's SpooledTemporaryFile may not have size until read.
    # We stream and enforce the limit during hashing/storage.
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_EVIDENCE_TYPES:
        raise SentinelError(
            f"Unsupported content type: {content_type}",
            status_code=400,
            detail={"allowed": sorted(ALLOWED_EVIDENCE_TYPES)},
        )


def compute_sha256(file_bytes: bytes) -> str:
    """Compute SHA-256 hex digest."""
    return hashlib.sha256(file_bytes).hexdigest()


def get_storage_path(sha256_hash: str, extension: str | None = None) -> Path:
    """Return a content-addressed storage path: storage/aa/bb/cc..."""
    base = Path(settings.EVIDENCE_STORAGE_PATH)
    if len(sha256_hash) < 4:
        raise SentinelError("Invalid hash length", status_code=500)

    # Two-level prefix to avoid a single massive directory.
    prefix_dir = base / sha256_hash[:2] / sha256_hash[2:4]
    prefix_dir.mkdir(parents=True, exist_ok=True)

    filename = sha256_hash
    if extension:
        filename = f"{sha256_hash}{extension}"

    return prefix_dir / filename


def safe_read(file: UploadFile) -> bytes:
    """Stream-read the upload with a strict size limit."""
    chunks = []
    total = 0
    chunk_size = 1024 * 1024  # 1 MB

    while True:
        chunk = file.file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_SIZE:
            raise SentinelError(
                "File exceeds maximum upload size",
                status_code=413,
                detail={"max_size": MAX_UPLOAD_SIZE},
            )
        chunks.append(chunk)

    return b"".join(chunks)


def get_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in (".eml", ".txt", ".msg"):
        return ext
    return ".bin"
