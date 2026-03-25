"""Normalize Mongo/BSON values so JSON/Pydantic never hits invalid UTF-8 bytes."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, cast
from uuid import UUID


def _decode_bytes(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def normalize_uuid(value: Any) -> Optional[UUID]:
    """Coerce UUID from str, UUID, or BSON Binary (16-byte UUID subtype)."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        s = value.strip()
        if len(s) in (32, 36):
            try:
                return UUID(s)
            except ValueError:
                return None
        return None
    try:
        from bson.binary import Binary

        if isinstance(value, Binary):
            b = bytes(value)
            if len(b) != 16:
                return None
            try:
                return value.as_uuid()
            except Exception:
                try:
                    return UUID(bytes=b)
                except ValueError:
                    return None
    except ImportError:
        pass
    if isinstance(value, (bytes, bytearray, memoryview)) and len(value) == 16:
        try:
            return UUID(bytes=bytes(value))
        except ValueError:
            return None
    return None


def sanitize_map_landmarks(raw: Any) -> List[Dict[str, Any]]:
    """Sanitize nested JSON and fix map pin `landmark_id` (UUID / BSON Binary)."""
    cleaned = sanitize_json(raw)
    if not isinstance(cleaned, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in cleaned:
        if not isinstance(item, dict):
            continue
        row = cast(Dict[str, Any], dict(item))
        lid = row.get("landmark_id")
        nu = normalize_uuid(lid)
        if lid is not None and nu is not None:
            row["landmark_id"] = str(nu)
        elif lid is not None:
            row["landmark_id"] = None
        out.append(row)
    return out


def sanitize_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        from bson.binary import Binary

        if isinstance(value, Binary):
            b = bytes(value)
            if len(b) == 16:
                nu = normalize_uuid(value)
                if nu is not None:
                    return str(nu)
            return _decode_bytes(b)
    except ImportError:
        pass
    if isinstance(value, (bytes, bytearray, memoryview)):
        return _decode_bytes(bytes(value))
    return str(value)


def _sanitize_key(k: Any) -> Any:
    if isinstance(k, str):
        return k
    try:
        from bson.binary import Binary

        if isinstance(k, Binary):
            b = bytes(k)
            if len(b) == 16:
                nu = normalize_uuid(k)
                if nu is not None:
                    return str(nu)
            return _decode_bytes(b)
    except ImportError:
        pass
    if isinstance(k, (bytes, bytearray, memoryview)):
        return _decode_bytes(bytes(k))
    return k


def sanitize_json(value: Any) -> Any:
    """Recursively convert bytes/Binary to str; preserve UUID/datetime/numbers."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, UUID):
        return value
    if isinstance(value, datetime):
        return value
    # BSON Binary subclasses bytes — must handle UUID before raw bytes decode
    try:
        from bson.binary import Binary

        if isinstance(value, Binary):
            b = bytes(value)
            if len(b) == 16:
                nu = normalize_uuid(value)
                if nu is not None:
                    return nu
            return _decode_bytes(b)
    except ImportError:
        pass
    if isinstance(value, (bytes, bytearray, memoryview)):
        return _decode_bytes(bytes(value))
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        out: Dict[Any, Any] = {}
        for k, v in value.items():
            out[_sanitize_key(k)] = sanitize_json(v)
        return out
    if isinstance(value, (list, tuple)):
        return [sanitize_json(x) for x in value]
    return value
