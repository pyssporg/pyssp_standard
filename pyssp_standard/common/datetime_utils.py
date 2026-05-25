from __future__ import annotations

from datetime import datetime


def format_generation_datetime(dt: datetime | str | None = None) -> str:
    """Return ISO 8601 UTC string for the given datetime.

    Args:
        dt: If None, returns "2000-01-01T00:00:00Z".
            If datetime, formats with "%Y-%m-%dT%H:%M:%SZ" (naive -> assumed UTC).
            If str, returned as-is.
    Returns:
        ISO 8601 UTC string, e.g. "2026-04-22T12:00:00Z".
    """
    if dt is None:
        return "2000-01-01T00:00:00Z"
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(dt)
