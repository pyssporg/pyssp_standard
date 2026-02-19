from pathlib import Path

from .archive_session import ArchiveSession

from .model.ssv_model import ParameterSet
from .model.ssd_model import SsdDocument, SsdParameterBinding
from .validator.semantic_validation import SsdBindingValidator
from .codec.ssd_codec import SsdBindingCodec
from .codec.ssv_hybrid_codec import Ssv2HybridCodec


class PublicSSD:
    """Public SSD API: XML codec usage only, no external artifact resolution."""

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
                self._doc = self._codec.parse(text)
            else:
                self._doc = SsdDocument(name="unnamed", version="1.0")
        return self._doc

    def validate(self):
        return self._validator.validate(self.document)

    def save(self):
        text = self._codec.serialize(self.document)
        self._session.write_text(text)


class PublicSSV:
    """Public SSV API focused on SSV file/model operations."""

    def __init__(self):
        self._codec = Ssv2HybridCodec()

    def load(self, ssv_path: str | Path) -> ParameterSet:
        session = ArchiveSession(Path(ssv_path), mode="r")
        return self._codec.parse(session.read_text())

    def save(self, ssv_path: str | Path, parameter_set: ParameterSet):
        session = ArchiveSession(Path(ssv_path), mode="a")
        session.write_text(
            self._codec.serialize(
                parameter_set,
                namespace_uri="http://ssp-standard.org/SSP1/SystemStructureParameterValues",
            )
        )

    def add_parameter(
        self,
        parameter_set: ParameterSet,
        *,
        name: str,
        value: float,
    ):
        if not any(p.name == name for p in parameter_set.parameters):
            parameter_set.add_real_parameter(name=name, value=value)


class PublicSSP:
    """SSP-level orchestrator resolving cross-file references.

    This class owns external artifact resolution by first parsing all involved
    XML files and then resolving references with explicit internal/external flags.
    """

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self._ssd_codec = SsdBindingCodec()
        self._public_ssv = PublicSSV()

    def load_ssd(self, ssd_path: str | Path) -> SsdDocument:
        ssd_path = self.root_dir / Path(ssd_path)
        session = ArchiveSession(ssd_path, mode="r")
        doc = self._ssd_codec.parse(session.read_text())
        self._resolve_bindings(doc, ssd_path)
        return doc

    def save_ssd(self, ssd_path: str | Path, doc: SsdDocument):
        ssd_path = self.root_dir / Path(ssd_path)
        ssd_session = ArchiveSession(ssd_path, mode="a")
        ssd_session.write_text(self._ssd_codec.serialize(doc))

        # Persist external parameter sets only at SSP orchestration level
        for binding in doc.parameter_bindings:
            if binding.is_inlined or not binding.external_path or binding.parameter_set is None:
                continue

            ext_path = ssd_path.parent / binding.external_path
            self._public_ssv.save(ext_path, binding.parameter_set)

    def _resolve_bindings(self, doc: SsdDocument, ssd_path: Path):
        for binding in doc.parameter_bindings:
            if binding.is_inlined:
                binding.is_resolved = binding.parameter_set is not None
                continue

            if not binding.is_inlined and binding.external_path:
                ext_path = ssd_path.parent / binding.external_path
                if ext_path.exists():
                    binding.parameter_set = self._public_ssv.load(ext_path)
                    binding.is_resolved = True
                else:
                    binding.parameter_set = None
                    binding.is_resolved = False
