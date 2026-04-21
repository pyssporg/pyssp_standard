from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, ClassVar, Iterable


@dataclass(frozen=True)
class ExternalReferenceField:
    codec: str
    path_attr: str
    value_attr: str
    resolved_attr: str
    predicate: Callable[[Any], bool] | None = None


class ExternalReferenceBinding:
    external_reference_fields: ClassVar[tuple[ExternalReferenceField, ...]] = ()

    def iter_external_reference_fields(self) -> Iterable[ExternalReferenceField]:
        for field in self.external_reference_fields:
            if field.predicate is not None and not field.predicate(self):
                continue
            if getattr(self, field.path_attr):
                yield field


def iter_external_reference_bindings(root: Any) -> Iterable[ExternalReferenceBinding]:
    if root is None or _is_leaf_value(root):
        return

    if isinstance(root, ExternalReferenceBinding):
        yield root

    if is_dataclass(root):
        for field in fields(root):
            yield from iter_external_reference_bindings(getattr(root, field.name))
        return

    if isinstance(root, dict):
        for value in root.values():
            yield from iter_external_reference_bindings(value)
        return

    if isinstance(root, (list, tuple, set)):
        for value in root:
            yield from iter_external_reference_bindings(value)


def _is_leaf_value(value: Any) -> bool:
    return isinstance(value, (str, bytes, int, float, bool))
