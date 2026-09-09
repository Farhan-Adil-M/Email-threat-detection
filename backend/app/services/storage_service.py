import hashlib
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.core.security import (
    compute_sha256,
    get_extension,
    get_storage_path,
    safe_read,
    sanitize_filename,
)
from app.models.evidence import EvidenceObject


class StorageService:
    def __init__(self):
        self.base_path = Path(settings.EVIDENCE_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def store_upload(self, case_id, file: UploadFile) -> EvidenceObject:
        """Persist an uploaded file by content hash and return an EvidenceObject."""
        original_filename = sanitize_filename(file.filename)
        file_bytes = safe_read(file)
        sha256_hash = compute_sha256(file_bytes)
        extension = get_extension(original_filename)
        storage_path = get_storage_path(sha256_hash, extension)

        # Write once; if file already exists, do not rewrite.
        if not storage_path.exists():
            storage_path.write_bytes(file_bytes)

        return EvidenceObject(
            case_id=case_id,
            type="email_raw",
            sha256=sha256_hash,
            storage_reference=str(storage_path.relative_to(self.base_path)),
            original_filename=original_filename,
            content_type=file.content_type or "application/octet-stream",
            size=len(file_bytes),
            sensitivity="confidential",
        )

    def read_by_hash(self, sha256_hash: str) -> bytes | None:
        """Read evidence bytes by hash if it exists."""
        candidates = list(self.base_path.rglob(f"{sha256_hash}*"))
        if not candidates:
            return None
        return candidates[0].read_bytes()

    def verify_hash(self, sha256_hash: str) -> bool:
        """Verify that stored content matches its recorded hash."""
        data = self.read_by_hash(sha256_hash)
        if data is None:
            return False
        return hashlib.sha256(data).hexdigest() == sha256_hash
