from abc import ABC, abstractmethod
from pathlib import Path

from shared.archive_session import ArchiveSession

from .parameter_model import ParameterSet
from .ssv_hybrid_codec import Ssv2HybridCodec


class ParameterSetStorage(ABC):
    @abstractmethod
    def load(self, *, context_path: Path, encoded_value: str) -> ParameterSet:
        raise NotImplementedError

    @abstractmethod
    def save(self, *, context_path: Path, model: ParameterSet, encoded_value: str | None = None) -> str:
        raise NotImplementedError


class InlineParameterSetStorage(ParameterSetStorage):
    def __init__(self):
        self._codec = Ssv2HybridCodec()

    def load(self, *, context_path: Path, encoded_value: str) -> ParameterSet:
        return self._codec.parse(encoded_value)

    def save(self, *, context_path: Path, model: ParameterSet, encoded_value: str | None = None) -> str:
        return self._codec.serialize(
            model,
            namespace_uri="http://ssp-standard.org/SSP1/SystemStructureDescription",
        )


class ExternalParameterSetStorage(ParameterSetStorage):
    def __init__(self):
        self._codec = Ssv2HybridCodec()

    def load(self, *, context_path: Path, encoded_value: str) -> ParameterSet:
        external_path = (context_path.parent / encoded_value).resolve()
        session = ArchiveSession(external_path, mode="r")
        return self._codec.parse(session.read_text())

    def save(self, *, context_path: Path, model: ParameterSet, encoded_value: str | None = None) -> str:
        if not encoded_value:
            raise ValueError("External storage requires an external path")

        external_path = (context_path.parent / encoded_value).resolve()
        session = ArchiveSession(external_path, mode="a")
        session.write_text(
            self._codec.serialize(
                model,
                namespace_uri="http://ssp-standard.org/SSP1/SystemStructureParameterValues",
            )
        )

        return encoded_value
