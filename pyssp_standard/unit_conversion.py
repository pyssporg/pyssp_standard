from __future__ import annotations


_BASE_UNITS: dict[str, dict[str, float | int]] = {
    "kg": {"kg": 1},
    "m": {"m": 1},
    "s": {"s": 1},
    "A": {"a": 1},
    "K": {"k": 1},
    "mol": {"mol": 1},
    "cd": {"cd": 1},
    "rad": {"rad": 1},
    "N": {"kg": 1, "m": 1, "s": -2},
}


def generate_base_unit(name: str) -> dict[str, float | int]:
    """Return a minimal base-unit definition for common unit names."""
    return dict(_BASE_UNITS.get(name, {}))
