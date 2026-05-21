from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar

from pyssp_standard.standard.version_routing import (
    StandardVersion,
    get_codec_and_validator,
    get_standard_version_from_file,
)

DocumentT = TypeVar("DocumentT")


class XmlDocument(Generic[DocumentT]):
    """Shared public-API facade behavior for XML-backed documents."""

    def __init__(self, path: str | Path, mode: str = "r",):
        self.path = Path(path)
        self.mode = mode
        self._document: DocumentT | None = None
        self._codec = None
        self._validator = None
        self._version = ""

    def __enter__(self):
        if self.mode == "w":
            self._document = self._create_document()
        else:
            self._document = self.load_document()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None and self.mode in {"w", "a"}:
            self.check_compliance()
            self.save_document()
        return False

    def get_codec_and_validator(self, family, format):
        if self.mode != "w":
            try:
                sv = get_standard_version_from_file(self.path)
                self._version = sv.version
            except FileNotFoundError:
                pass

        # Dispatch codec and validator
        codec_type, validator_type = get_codec_and_validator(
            StandardVersion(family=family, format=format, version=self._version)
        )
        return codec_type(), validator_type()

    @property
    def xml(self) -> DocumentT:
        if self._document is None:
            raise RuntimeError("XML document is not loaded")
        return self._document

    def check_compliance(self):
        xml_text = self._codec.serialize(self.xml)
        self._validator.validate(self.xml, xml_text)
        return True

    def load_document(self) -> DocumentT:
        if not self.path.exists():
            return self._create_document()

        text = self.path.read_text(encoding="utf-8")
        return self._codec.parse(text)
    
    def from_xml(self, text):
        self._document = self._codec.parse(text)

    def save_document(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self._codec.serialize(self.xml), encoding="utf-8")

    def _create_document(self) -> DocumentT:
        raise NotImplementedError
    

