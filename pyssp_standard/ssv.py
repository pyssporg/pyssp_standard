"""SSV (ParameterSet) facade — version-aware through version routing."""

from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_document import XmlDocument
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet
from pyssp_standard.standard.ssp2.model.ssv_model import Ssp2ParameterSet
from pyssp_standard.standard.version_routing import (
    StandardVersion,
    get_codec_and_validator,
    get_standard_version_from_file,
)


class SSV(XmlDocument[Ssp1ParameterSet | Ssp2ParameterSet]):
    """SSV (ParameterSet) facade — version-aware through version routing."""

    def __init__(self, path: str | Path, mode: str = "r", version: str | None = None) -> None:
        super().__init__(path, mode)
        self._version = version or "1.0"

        self._codec, self._validator = self.get_codec_and_validator("SSP", "SSV")


    def _create_document(self) -> Ssp1ParameterSet | Ssp2ParameterSet:
        if self._version == "2.0":
            return Ssp2ParameterSet(name=self.path.stem or "parameters", version="2.0")
        return Ssp1ParameterSet(name=self.path.stem or "parameters", version="1.0")