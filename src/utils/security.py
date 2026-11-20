"""Security checks, file sanitization, and safety guards."""

import os
from pathlib import Path

from config.settings import config


class SecurityValidationError(Exception):
    """Raised when file validation fails security or structural limits."""


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename to prevent directory traversal or malformed names."""
    base = os.path.basename(filename)
    clean_name = "".join(c for c in base if c.isalnum() or c in (".", "_", "-", " ", "()")).strip()
    return clean_name or "dataset.csv"


def validate_file_metadata(filename: str, file_size_bytes: int) -> tuple[bool, str]:
    """Validate file extension and file size against configured limits.

    Returns (is_valid, error_message).
    """
    clean_name = sanitize_filename(filename)
    ext = Path(clean_name).suffix.lstrip(".").lower()

    if ext not in config.allowed_extensions:
        allowed = ", ".join(config.allowed_extensions).upper()
        return False, f"نوع الملف '.{ext}' غير مدعوم. الصيغ المدعومة هي: {allowed}"

    max_bytes = config.max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        return (
            False,
            f"حجم الملف ({file_size_bytes / (1024 * 1024):.1f} MB) يتجاوز الحد الأقصى المسموح به ({config.max_file_size_mb} MB).",
        )

    if file_size_bytes == 0:
        return False, "الملف المرفوع فارغ (0 بايت)."

    return True, ""
