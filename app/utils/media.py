"""Public URLs for uploaded assets (served under /uploads)."""
from __future__ import annotations

from typing import Optional


def public_image_url(path: Optional[str]) -> Optional[str]:
    """
    Normalize stored path for API JSON. Accepts absolute http(s) URLs or site-relative paths like /uploads/...
    """
    if path is None:
        return None
    s = str(path).strip()
    if not s:
        return None
    if s.startswith("http://") or s.startswith("https://"):
        return s
    if not s.startswith("/"):
        s = "/" + s
    return s
