from __future__ import annotations

from pathlib import Path

from pyssp_standard.ssm import SSM
from pyssp_standard.standard.ssp1.codec.ssd_xml_codec import Ssp1SsdXmlCodec
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1DefaultExperiment,
    Ssd1ParameterBinding,
    Ssd1SystemStructureDescription,
    Ssd1System,
)
from pyssp_standard.standard.ssp1.validation import Ssp1SsdValidator
from pyssp_standard.ssv import SSV
from pyssp_standard.common.xml_document import XmlDocumentFacade


Connection = Ssd1Connection
System = Ssd1System
DefaultExperiment = Ssd1DefaultExperiment
Component = Ssd1Component
Connector = Ssd1Connector
ParameterBinding = Ssd1ParameterBinding


class SSD(XmlDocumentFacade[Ssd1SystemStructureDescription]):
    """Public SSD facade.

    By default this is a plain XML facade. When constructed with
    `resolve_external_references=True`, it also performs archive-relative
    orchestration for external parameter sets and parameter mappings.
    """

    def __init__(
        self,
        path: str | Path,
        mode: str = "r",
        *,
        resolve_external_references: bool = False,
        reference_base_dir: str | Path | None = None,
    ):
        super().__init__(path, mode)
        self._codec = Ssp1SsdXmlCodec()
        self._validator = Ssp1SsdValidator()
        self._resolve_external_references = resolve_external_references
        self._reference_base_dir = Path(reference_base_dir) if reference_base_dir is not None else self.path.parent

    def __enter__(self):
        super().__enter__()
        if self._resolve_external_references:
            self._load_external_references()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None and self.mode in {"w", "a"} and self._resolve_external_references:
            self._persist_external_references()
        return super().__exit__(exc_type, exc, tb)

    def _create_document(self) -> Ssd1SystemStructureDescription:
        return Ssd1SystemStructureDescription(name=self.path.stem or "system", version="1.0", system=Ssd1System(name="system"))

    @property
    def name(self) -> str:
        return self.document.name

    @name.setter
    def name(self, value: str) -> None:
        self.document.name = value

    @property
    def version(self) -> str:
        return self.document.version

    @version.setter
    def version(self, value: str) -> None:
        self.document.version = value

    @property
    def system(self) -> Ssd1System | None:
        return self.document.system

    @system.setter
    def system(self, value: Ssd1System | None) -> None:
        self.document.system = value

    @property
    def default_experiment(self) -> Ssd1DefaultExperiment | None:
        return self.document.default_experiment

    @default_experiment.setter
    def default_experiment(self, value: Ssd1DefaultExperiment | None) -> None:
        self.document.default_experiment = value

    def add_connection(self, connection: Ssd1Connection) -> Ssd1Connection:
        return self.document.add_connection(connection)

    def remove_connection(self, connection: Ssd1Connection) -> None:
        self.document.remove_connection(connection)

    def list_connectors(self, parent: str | None = None):
        return self.document.list_connectors(parent=parent)

    def connections(self):
        return self.document.connections()

    @property
    def parameter_bindings(self):
        return self.document.parameter_bindings

    def _load_external_references(self) -> None:
        for binding in self.parameter_bindings:
            if not binding.is_inlined and binding.external_path:
                external_path = self._reference_base_dir / binding.external_path
                if external_path.exists():
                    try:
                        with SSV(external_path, mode="r") as ssv:
                            binding.parameter_set = ssv.document
                        binding.is_resolved = True
                    except Exception:
                        binding.parameter_set = None
                        binding.is_resolved = False
                else:
                    binding.parameter_set = None
                    binding.is_resolved = False

            if binding.parameter_mapping_path:
                mapping_path = self._reference_base_dir / binding.parameter_mapping_path
                if mapping_path.exists():
                    try:
                        with SSM(mapping_path, mode="r") as ssm:
                            binding.parameter_mapping = ssm.document
                        binding.is_mapping_resolved = True
                    except Exception:
                        binding.parameter_mapping = None
                        binding.is_mapping_resolved = False
                else:
                    binding.parameter_mapping = None
                    binding.is_mapping_resolved = False

    def _persist_external_references(self) -> None:
        for binding in self.parameter_bindings:
            if not binding.is_inlined and binding.external_path and binding.parameter_set is not None:
                external_path = self._reference_base_dir / binding.external_path
                with SSV(external_path, mode="w") as ssv:
                    ssv._document = binding.parameter_set

            if binding.parameter_mapping_path and binding.parameter_mapping is not None:
                mapping_path = self._reference_base_dir / binding.parameter_mapping_path
                with SSM(mapping_path, mode="w") as ssm:
                    ssm._document = binding.parameter_mapping
