from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

from pyssp_standard.standard.ssp1.codec.ssd_codec import Ssp1SsdCodec
from pyssp_standard.standard.ssp1.operations.ssd_parameters import extend_component_parametersets
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
from pyssp_standard.common.xml_document import XmlDocument

from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1DocumentMetadata
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


    def extend_component_parameterset(
        self,
        parameters_by_component: Mapping[
            str,
            Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object]],
        ],
    ) -> None:
        """Extend inline parameter sets for components by component name.

        Example:
            ssd.extend_component_parameterset({
                "controller": {"gain": 2.0, "enabled": True},
                "plant": [("offset", -1.0)],
            })
        """
        extend_component_parametersets(self.xml, parameters_by_component)

    def extend_system_parameterset(
        self,
        parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object]],
        *,
        binding_name: str | None = None,
        prefix: str | None = None,
        version: str = "1.0",
        metadata: Ssp1DocumentMetadata | None = None,
    ) -> None:
        """Extend the top-level system's inline parameter set."""
        if self.xml.system is None:
            raise RuntimeError("Cannot extend a parameter set without a system")
        self.xml.system.extend_inline_parameterset(
            parameters,
            binding_name=binding_name,
            prefix=prefix,
            version=version,
            metadata=metadata,
        )



