from __future__ import annotations

from dataclasses import dataclass, field

from pyssp_standard.standard.ssp1.model.ssc_model import (
    Ssp1Annotation,
    Ssp1DocumentMetadata,
    Ssp1Enumeration,
    Ssp1EnumerationItem,
    Ssp1Unit,
)
from pyssp_standard.standard.ssp1.model.common_collections import (
    add_enumeration as add_common_enumeration,
    add_unit as add_common_unit,
    get_unit as get_common_unit,
)


@dataclass
class Ssp1DictionaryEntry:
    name: str
    type_name: str
    attributes: dict[str, str] = field(default_factory=dict)
    id: str | None = None
    description: str | None = None
    annotations: list[Ssp1Annotation] = field(default_factory=list)


@dataclass
class Ssp1SignalDictionary:
    version: str
    metadata: Ssp1DocumentMetadata = field(default_factory=Ssp1DocumentMetadata)
    entries: list[Ssp1DictionaryEntry] = field(default_factory=list)
    enumerations: list[Ssp1Enumeration] = field(default_factory=list)
    units: list[Ssp1Unit] = field(default_factory=list)

    def add_entry(
        self,
        name: str,
        type_name: str = "Real",
        *,
        unit: str | None = None,
        enumeration: str | None = None,
        mimetype: str | None = None,
    ) -> Ssp1DictionaryEntry:
        attributes: dict[str, str] = {}
        if unit is not None:
            attributes["unit"] = unit
        if enumeration is not None:
            attributes["name"] = enumeration
        if mimetype is not None:
            attributes["mime-type"] = mimetype

        entry = Ssp1DictionaryEntry(name=name, type_name=type_name, attributes=attributes)
        self.entries.append(entry)
        return entry

    def add_dictionary_entry(
        self,
        name: str,
        *,
        ptype: str = "Real",
        value: dict[str, str] | None = None,
    ) -> Ssp1DictionaryEntry:
        entry = Ssp1DictionaryEntry(name=name, type_name=ptype, attributes=dict(value or {}))
        self.entries.append(entry)
        return entry

    def add_unit(self, name: str, base_unit: dict[str, object] | None = None) -> Ssp1Unit:
        return add_common_unit(self.units, name, base_unit)

    def get_unit(self, name: str) -> Ssp1Unit | None:
        return get_common_unit(self.units, name)

    def add_enumeration(self, name: str, items: list[Ssp1EnumerationItem]) -> Ssp1Enumeration:
        return add_common_enumeration(self.enumerations, name, items)
