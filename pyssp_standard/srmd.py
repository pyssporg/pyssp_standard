from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pyssp_standard.common.xml_document import XmlDocument
from pyssp_standard.standard.ssp1.codec.srmd_codec import Ssp1SrmdCodec
from pyssp_standard.standard.ssp1.model.srmd_model import (
    Ssp1Classification,
    Ssp1ClassificationEntry,
    Ssp1SimulationResourceMetaData,
)
from pyssp_standard.standard.ssp1.validation import Ssp1SrmdValidator


Classification = Ssp1Classification
ClassificationEntry = Ssp1ClassificationEntry
SimulationResourceMetaData = Ssp1SimulationResourceMetaData


class SRMD(XmlDocument[Ssp1SimulationResourceMetaData]):
    """Public SRMD facade following the layered SSP1 package layout."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SrmdCodec()
        self._validator = Ssp1SrmdValidator()

    def _create_document(self) -> Ssp1SimulationResourceMetaData:
        return Ssp1SimulationResourceMetaData(
            version="1.0.0-beta2",
            name=self.path.stem or "resource-meta-data",
        )

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the XML document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        from pyssp_standard.common.datetime_utils import format_generation_datetime

        self.xml.metadata.generation_date_and_time = format_generation_datetime(dt)
