from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar


DocumentT = TypeVar("DocumentT")


class XmlDocument(Generic[DocumentT]):
    """Shared public-API facade behavior for XML-backed documents."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._document: DocumentT | None = None
        self._codec = None
        self._validator = None

    def __enter__(self):
        if self.mode == "w":
            self._document = self._create_document()
        else:
            self._document = self.load_document()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None and self.mode in {"w", "a"}:
            self.save_document()
        return False

    @property
    def document(self) -> DocumentT:
        if self._document is None:
            raise RuntimeError("XML document is not loaded")
        return self._document

    @property
    def metadata(self):
        return self.document.metadata

    def check_compliance(self):
        xml_text = self._codec.serialize(self.document)
        self._validator.validate(self.document, xml_text)
        return True

    def load_document(self) -> DocumentT:
        if not self.path.exists():
            return self._create_document()

        text = self.path.read_text(encoding="utf-8")
        return self._codec.parse(text)

    def save_document(self):
        self.path.write_text(self._codec.serialize(self.document), encoding="utf-8")

    def _create_document(self) -> DocumentT:
        raise NotImplementedError

