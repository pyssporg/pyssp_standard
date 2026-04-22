from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_document import XmlDocument
from pyssp_standard.standard.ssp1.codec.ssb_codec import Ssp1SsbCodec
from pyssp_standard.standard.ssp1.model.ssb_model import Ssp1SignalDictionary
from pyssp_standard.standard.ssp1.validation import Ssp1SsbValidator


class SSB(XmlDocument[Ssp1SignalDictionary]):
    """Public SSB facade following the same layered pattern as the other SSP1 documents."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsbCodec()
        self._validator = Ssp1SsbValidator()

    def _create_document(self) -> Ssp1SignalDictionary:
        return Ssp1SignalDictionary(version="1.0")
