from pathlib import Path

from shared.archive_session import ArchiveSession

from .ssd_handwritten_codec import SsdHandwrittenCodec
from .ssd_model import SsdDocument
from .ssd_semantic_validation import SsdSemanticValidator


class PublicSSD:
    """Public API facade backed by handwritten SSD codec path."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self._session = ArchiveSession(Path(path), mode=mode)
        self._codec = SsdHandwrittenCodec()
        self._validator = SsdSemanticValidator()
        self._doc: SsdDocument | None = None

    @property
    def document(self) -> SsdDocument:
        if self._doc is None:
            xml = self._session.read_text()
            if xml.strip():
                self._doc = self._codec.parse(xml)
            else:
                self._doc = SsdDocument(name="unnamed", version="1.0")
        return self._doc

    def add_component(self, name: str, source: str):
        self.document.add_component(name, source)

    def connect(self, start_element: str, start_connector: str, end_element: str, end_connector: str):
        self.document.add_connection(start_element, start_connector, end_element, end_connector)

    def validate(self):
        return self._validator.validate(self.document)

    def save(self):
        xml = self._codec.serialize(self.document)
        self._session.write_text(xml)
