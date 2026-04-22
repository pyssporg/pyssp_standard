from __future__ import annotations

from dataclasses import is_dataclass
from pathlib import Path
from typing import Any, Generic, TypeVar

from pyssp_standard.common.zip_archive import DirectoryRuntime


FacadeT = TypeVar("FacadeT")


class ExternalReferenceSpec:
    def __init__(self, owner_type: type[Any], source_attr: str, document_attr: str, facade_type: type[Any]):
        self.owner_type = owner_type
        self.source_attr = source_attr
        self.document_attr = document_attr
        self.facade_type = facade_type


class _ResolvedExternalDocument:
    def __init__(self, spec: ExternalReferenceSpec, path: Path, document: Any):
        self.spec = spec
        self.path = path
        self.document = document


class _ResolvedPlacement:
    def __init__(self, owner: Any, resolved: _ResolvedExternalDocument):
        self.owner = owner
        self.resolved = resolved


class DocumentRuntime(Generic[FacadeT]):
    def __init__(
        self,
        runtime: DirectoryRuntime,
        *,
        document_path: str,
        document_type: type[FacadeT],
        external_reference_specs: tuple[ExternalReferenceSpec, ...] = (),
        mode: str = "r",
    ):
        self._runtime = runtime
        self._document_path = runtime.resolve(document_path)
        self._mode = mode
        self._document = document_type(self._document_path, mode=mode)
        self._external_reference_specs = external_reference_specs
        self._resolved_documents: dict[tuple[type[Any], Path], _ResolvedExternalDocument] = {}
        self._resolved_placements: list[_ResolvedPlacement] = []

    def __enter__(self) -> FacadeT:
        self._document.__enter__()
        self._enter_external_documents()
        return self._document

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self._leave_external_documents(persist=self._mode in {"w", "a"})
            else:
                self._leave_external_documents(persist=False)
        finally:
            self._resolved_documents.clear()
            self._resolved_placements.clear()
        return self._document.__exit__(exc_type, exc, tb)

    @property
    def path(self) -> Path:
        return self._document_path

    def _enter_external_documents(self) -> None:
        for owner, spec in self._iter_external_reference_targets(self._document.document):
            resolved = self._load_external_document(owner, spec)
            if resolved is None:
                self._set_attr(owner, spec.document_attr, None)
                continue
            self._set_attr(owner, spec.document_attr, resolved.document)
            self._resolved_placements.append(_ResolvedPlacement(owner=owner, resolved=resolved))

    def _leave_external_documents(self, *, persist: bool) -> None:
        persisted_paths: set[tuple[type[Any], Path]] = set()
        for placement in self._resolved_placements:
            owner = placement.owner
            spec = placement.resolved.spec
            document = self._get_attr(owner, spec.document_attr)
            cache_key = (spec.facade_type, placement.resolved.path)

            if persist and document is not None and cache_key not in persisted_paths:
                self._save_external_document(placement.resolved.path, spec.facade_type, document)
                persisted_paths.add(cache_key)

            self._set_attr(owner, spec.document_attr, None)

    def _iter_external_reference_targets(self, root: Any):
        visited: set[int] = set()
        stack = [root]
        while stack:
            current = stack.pop()
            if current is None:
                continue
            current_id = id(current)
            if current_id in visited:
                continue
            visited.add(current_id)

            for spec in self._external_reference_specs:
                if isinstance(current, spec.owner_type):
                    source = self._get_attr(current, spec.source_attr)
                    if source:
                        yield current, spec

            if is_dataclass(current):
                stack.extend(value for value in vars(current).values() if not self._is_leaf_value(value))
                continue

            if isinstance(current, dict):
                stack.extend(value for value in current.values() if not self._is_leaf_value(value))
                continue

            if isinstance(current, (list, tuple, set)):
                stack.extend(value for value in current if not self._is_leaf_value(value))

    def _load_external_document(self, owner: Any, spec: ExternalReferenceSpec) -> _ResolvedExternalDocument | None:
        source = self._get_attr(owner, spec.source_attr)
        if not source:
            return None

        path = self._runtime.resolve(source)
        cache_key = (spec.facade_type, path)
        if cache_key in self._resolved_documents:
            return self._resolved_documents[cache_key]
        if not path.exists():
            return None

        try:
            with spec.facade_type(path, mode="r") as facade:
                resolved = _ResolvedExternalDocument(spec=spec, path=path, document=facade.document)
        except Exception:
            return None

        self._resolved_documents[cache_key] = resolved
        return resolved

    @staticmethod
    def _save_external_document(path: Path, facade_type: type[Any], document: Any) -> None:
        with facade_type(path, mode="w") as facade:
            facade._document = document

    @staticmethod
    def _get_attr(owner: Any, attr_name: str) -> Any:
        if hasattr(owner, attr_name):
            return getattr(owner, attr_name)
        return None

    @staticmethod
    def _set_attr(owner: Any, attr_name: str, value: Any) -> None:
        if hasattr(owner, attr_name):
            setattr(owner, attr_name, value)

    @staticmethod
    def _is_leaf_value(value: Any) -> bool:
        return isinstance(value, (str, bytes, int, float, bool, Path))
