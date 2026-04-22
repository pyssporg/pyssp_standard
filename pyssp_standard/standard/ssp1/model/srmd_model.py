from __future__ import annotations

from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1DocumentMetadata


@dataclass
class Ssp1ClassificationEntry:
    keyword: str
    text: str = ""
    type: str = "text/plain"
    href: str | None = None
    linked_type: str | None = None
    id: str | None = None
    description: str | None = None
    content: list[ET.Element] = field(default_factory=list)


@dataclass
class Ssp1Classification:
    type: str | None = None
    entries: list[Ssp1ClassificationEntry] = field(default_factory=list)
    href: str | None = None
    linked_type: str | None = None
    id: str | None = None
    description: str | None = None

    def add_entry(
        self,
        keyword: str,
        *,
        text: str = "",
        type: str = "text/plain",
        href: str | None = None,
        linked_type: str | None = None,
        content: list[ET.Element] | None = None,
    ) -> Ssp1ClassificationEntry:
        entry = Ssp1ClassificationEntry(
            keyword=keyword,
            text=text,
            type=type,
            href=href,
            linked_type=linked_type,
            content=list(content or []),
        )
        self.entries.append(entry)
        return entry


@dataclass
class Ssp1SimulationResourceMetaData:
    version: str
    name: str
    metadata: Ssp1DocumentMetadata = field(default_factory=Ssp1DocumentMetadata)
    data: str | None = None
    checksum: str | None = None
    checksum_type: str | None = None
    classifications: list[Ssp1Classification] = field(default_factory=list)

    def add_classification(self, type: str | None = None, **kwargs) -> Ssp1Classification:
        classification = Ssp1Classification(type=type, **kwargs)
        self.classifications.append(classification)
        return classification
