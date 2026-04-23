"""Document orchestration layer.

Purpose:
- Bind a parsed XML document to a domain aggregate.
- Synchronize domain state back into XML for serialization.

Boundary:
- Knows the XML root and the bound aggregate.
- Exposes the bound domain aggregate but does not own domain behavior.
- Does not contain specialized field mapping logic; that stays in projection.py.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from layer_example.domain import Catalog
from layer_example.projection import publish_catalog, read_catalog
from layer_example.xml_model import parse_xml, serialize


class CatalogDocument:
    def __init__(self, root: ET.Element, catalog: Catalog) -> None:
        self.root = root
        self.catalog = catalog

    @classmethod
    def from_xml(cls, xml_text: str) -> "CatalogDocument":
        root = parse_xml(xml_text)
        return cls(root=root, catalog=read_catalog(root))

    def apply(self) -> None:
        publish_catalog(self.catalog, self.root)

    def to_xml(self) -> str:
        self.apply()
        return serialize(self.root)
