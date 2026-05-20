"""Standalone external reference discovery extracted from DocumentRuntime.

This module contains the tree-walking logic that was previously an
instance method of DocumentRuntime, refactored into a pure function
so it can be tested independently.
"""

from __future__ import annotations

from dataclasses import is_dataclass
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pyssp_standard.common.document_runtime import ExternalReferenceSpec


def discover_external_references(
    root: Any,
    specs: tuple[ExternalReferenceSpec, ...],
) -> list[tuple[Any, ExternalReferenceSpec]]:
    """Walk a dataclass tree and yield (owner, spec) pairs for every
    element that matches one of the given external reference specs.

    This is the extracted core of ``DocumentRuntime._iter_external_reference_targets``.
    """
    visited: set[int] = set()
    stack = [root]
    results: list[tuple[Any, ExternalReferenceSpec]] = []

    while stack:
        current = stack.pop()
        if current is None:
            continue
        current_id = id(current)
        if current_id in visited:
            continue
        visited.add(current_id)

        for spec in specs:
            if isinstance(current, spec.owner_type):
                source = _get_attr(current, spec.source_attr)
                if source:
                    results.append((current, spec))

        if is_dataclass(current):
            stack.extend(
                value for value in vars(current).values()
                if not _is_leaf_value(value)
            )
            continue

        if isinstance(current, dict):
            stack.extend(
                value for value in current.values()
                if not _is_leaf_value(value)
            )
            continue

        if isinstance(current, (list, tuple, set)):
            stack.extend(
                value for value in current
                if not _is_leaf_value(value)
            )

    return results


def _get_attr(owner: Any, attr_name: str) -> Any:
    """Safely get an attribute, returning None if it doesn't exist."""
    if hasattr(owner, attr_name):
        return getattr(owner, attr_name)
    return None


def _is_leaf_value(value: Any) -> bool:
    """Return True if *value* is a primitive that cannot contain references."""
    return isinstance(value, (str, bytes, int, float, bool, Path))