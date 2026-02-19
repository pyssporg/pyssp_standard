from pathlib import Path

from shared.archive_session import ArchiveSession

from .semantic_validation import SsdBindingValidator
from .ssd_codec import SsdBindingCodec
from .ssd_model import SsdDocument, SsdParameterBinding


class PublicSSD:
    """Unified public API showing both inline and external parameter bindings."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self._path = Path(path)
        self._session = ArchiveSession(self._path, mode=mode)
        self._codec = SsdBindingCodec()
        self._validator = SsdBindingValidator()
        self._doc: SsdDocument | None = None

    @property
    def document(self) -> SsdDocument:
        if self._doc is None:
            text = self._session.read_text()
            if text.strip():
                self._doc = self._codec.parse(text, context_path=self._path)
            else:
                self._doc = SsdDocument(name="unnamed", version="1.0")
        return self._doc

    def validate(self):
        return self._validator.validate(self.document)

    def add_parameter(self, *, target: str, mode: str, name: str, value: float, external_path: str | None = None):
        binding = next((b for b in self.document.parameter_bindings if b.target == target and b.mode == mode), None)
        if binding is None:
            binding = SsdParameterBinding(target=target, mode=mode, external_path=external_path)
            self.document.parameter_bindings.append(binding)

        if binding.parameter_set is None:
            from .parameter_model import ParameterSet

            binding.parameter_set = ParameterSet(name=f"{target}_params", version="2.0")

        if not any(p.name == name for p in binding.parameter_set.parameters):
            binding.parameter_set.add_real_parameter(name=name, value=value)

    def save(self):
        text = self._codec.serialize(self.document, context_path=self._path)
        self._session.write_text(text)
