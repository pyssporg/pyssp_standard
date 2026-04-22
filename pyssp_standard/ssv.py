from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.codec.ssv_codec import Ssp1SsvCodec
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet
from pyssp_standard.standard.ssp1.validation import Ssp1SsvValidator
from pyssp_standard.common.xml_document import XmlDocument


class SSV(XmlDocument[Ssp1ParameterSet]):
    """Public SSV facade following the layered package layout."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsvCodec()
        self._validator = Ssp1SsvValidator()

    def _create_document(self) -> Ssp1ParameterSet:
        return Ssp1ParameterSet(name=self.path.stem or "parameters", version="1.0")
