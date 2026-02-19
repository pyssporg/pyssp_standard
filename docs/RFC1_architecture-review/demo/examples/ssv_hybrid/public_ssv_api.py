from pathlib import Path

from shared.archive_session import ArchiveSession

from .ssv_hybrid_codec import Ssv2HybridCodec
from .ssv_model import ParameterSet
from .ssv_semantic_validation import SemanticValidator


class PublicSSV:
    """Public compatibility facade exposing a stable API shape."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self._session = ArchiveSession(Path(path), mode=mode)
        self._codec = Ssv2HybridCodec()
        self._validator = SemanticValidator()
        self._model: ParameterSet | None = None

    @property
    def model(self) -> ParameterSet:
        if self._model is None:
            xml = self._session.read_text()
            if xml.strip():
                self._model = self._codec.parse(xml)
            else:
                self._model = ParameterSet(name="unnamed", version="2.0")
        return self._model

    @property
    def version(self) -> str:
        return self.model.version

    def add_parameter(self, name: str, value: float):
        self.model.add_real_parameter(name, value)

    def validate(self):
        return self._validator.validate_parameter_set(self.model)

    def save(self):
        xml = self._codec.serialize(self.model)
        self._session.write_text(xml)
