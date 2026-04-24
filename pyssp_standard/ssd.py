from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

from pyssp_standard.common.document_runtime import DocumentRuntime, ExternalReferenceSpec
from pyssp_standard.standard.ssp1.codec.ssd_codec import Ssp1SsdCodec
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1DefaultExperiment,
    Ssd1ParameterBinding,
    Ssd1ParameterMappingReference,
    Ssd1SystemStructureDescription,
    Ssd1System,
)
from pyssp_standard.standard.ssp1.validation import Ssp1SsdValidator
from pyssp_standard.common.xml_document import XmlDocument
from pyssp_standard.common.archive_runtime import DirectoryRuntime
from pyssp_standard.ssm import SSM
from pyssp_standard.ssv import SSV
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter


Connection = Ssd1Connection
System = Ssd1System
DefaultExperiment = Ssd1DefaultExperiment
Component = Ssd1Component
Connector = Ssd1Connector
ParameterBinding = Ssd1ParameterBinding


class SSD(XmlDocument[Ssd1SystemStructureDescription]):
    """Public SSD facade.

    This facade is intentionally limited to SSD file/model operations.
    Cross-file dependency resolution belongs to the SSP archive layer.
    """

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsdCodec()
        self._validator = Ssp1SsdValidator()

    def _create_document(self) -> Ssd1SystemStructureDescription:
        return Ssd1SystemStructureDescription(name=self.path.stem or "system", version="1.0", system=Ssd1System(name="system"))

    def extend_parameterset(
        self,
        parameters_by_component: Mapping[
            str,
            Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object] | Mapping[str, object]],
        ],
    ) -> None:
        system = self.xml.system
        if system is None:
            raise RuntimeError("Cannot extend a parameter set without a system")

        components_by_name = {
            element.name: element
            for element in system.elements
            if isinstance(element, Ssd1Component)
        }

        for component_name, parameters in parameters_by_component.items():
            component = components_by_name.get(component_name)
            if component is None:
                raise KeyError(f"Component not found in system '{system.name}': {component_name}")
            component.extend_inline_parameterset(parameters)


EXTERNAL_REFERENCE_SPECS = (
    ExternalReferenceSpec(
        owner_type=Ssd1ParameterBinding,
        source_attr="source",
        document_attr="parameter_set",
        facade_type=SSV,
    ),
    ExternalReferenceSpec(
        owner_type=Ssd1ParameterMappingReference,
        source_attr="source",
        document_attr="mapping",
        facade_type=SSM,
    ),
)


class SsdRuntime(DocumentRuntime[SSD]):
    """Archive-level SSD facade with dependency resolution."""

    def __init__(self, runtime: DirectoryRuntime, ssd_path: str = "SystemStructure.ssd", mode: str = "r"):
        super().__init__(
            runtime,
            document_path=ssd_path,
            document_type=SSD,
            external_reference_specs=EXTERNAL_REFERENCE_SPECS,
            mode=mode,
        )
