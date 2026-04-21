from __future__ import annotations

from dataclasses import dataclass, field

from lxml import etree


SSC_NS = "http://ssp-standard.org/SSP1/SystemStructureCommon"


@dataclass
class Transformation:
    type_name: str
    attributes: dict[str, object] = field(default_factory=dict)

    def element(self):
        element = etree.Element(f"{{{SSC_NS}}}{self.type_name}", nsmap={"ssc": SSC_NS})
        for key, value in self.attributes.items():
            element.set(key, str(value))
        return element
