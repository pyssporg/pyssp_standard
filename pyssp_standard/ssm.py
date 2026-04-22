from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.codec.ssm_codec import Ssp1SsmCodec
from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1Transformation
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping
from pyssp_standard.standard.ssp1.validation import Ssp1SsmValidator
from pyssp_standard.common.xml_document import XmlDocument


class SSM(XmlDocument[Ssp1ParameterMapping]):
    """Public SSM facade following the same layered pattern as SSV."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsmCodec()
        self._validator = Ssp1SsmValidator()

    def _create_document(self) -> Ssp1ParameterMapping:
        return Ssp1ParameterMapping(version="1.0")


