from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.codec.xml_utils import (
    NS_SSC,
    append_annotations,
    apply_metadata_attributes,
    clone_element,
    parse_metadata_attributes,
    qname,
)
from pyssp_standard.standard.ssp1.model.srmd_model import (
    Ssp1Classification,
    Ssp1ClassificationEntry,
    Ssp1SimulationResourceMetaData,
)


NS_SRMD = "http://ssp-standard.org/SSPTraceability1/SimulationResourceMetaData"
NS_STC = "http://ssp-standard.org/SSPTraceability1/SSPTraceabilityCommon"
NS_XLINK = "http://www.w3.org/1999/xlink"

XLINK_TYPE = qname(NS_XLINK, "type")
XLINK_HREF = qname(NS_XLINK, "href")


class Ssp1SrmdCodec:
    def parse(self, xml_text: str) -> Ssp1SimulationResourceMetaData:
        root = ET.fromstring(xml_text)
        document = Ssp1SimulationResourceMetaData(
            version=root.attrib["version"],
            name=root.attrib["name"],
            metadata=parse_metadata_attributes(root),
            data=root.attrib.get("data"),
            checksum=root.attrib.get("checksum"),
            checksum_type=root.attrib.get("checksumType"),
        )
        document.classifications = [
            self._parse_classification(element)
            for element in root.findall(qname(NS_STC, "Classification"))
        ]
        return document

    def serialize(self, document: Ssp1SimulationResourceMetaData) -> str:
        root = ET.Element(qname(NS_SRMD, "SimulationResourceMetaData"))
        root.set("version", document.version)
        root.set("name", document.name)
        if document.data is not None:
            root.set("data", document.data)
        if document.checksum is not None:
            root.set("checksum", document.checksum)
        if document.checksum_type is not None:
            root.set("checksumType", document.checksum_type)
        apply_metadata_attributes(root, document.metadata)
        for classification in document.classifications:
            root.append(self._serialize_classification(classification))
        append_annotations(root, document.metadata.annotations, NS_STC)
        return self._render_xml(root)

    def _parse_classification(self, element: ET.Element) -> Ssp1Classification:
        return Ssp1Classification(
            type=element.attrib.get("type"),
            entries=[
                self._parse_classification_entry(child)
                for child in element.findall(qname(NS_STC, "ClassificationEntry"))
            ],
            href=element.attrib.get(XLINK_HREF),
            linked_type=element.attrib.get("linkedType"),
            id=element.attrib.get("id"),
            description=element.attrib.get("description"),
        )

    def _serialize_classification(self, classification: Ssp1Classification) -> ET.Element:
        element = ET.Element(qname(NS_STC, "Classification"))
        if classification.type is not None:
            element.set("type", classification.type)
        self._set_link_attributes(element, href=classification.href, linked_type=classification.linked_type)
        if classification.id is not None:
            element.set("id", classification.id)
        if classification.description is not None:
            element.set("description", classification.description)
        for entry in classification.entries:
            element.append(self._serialize_classification_entry(entry))
        return element

    def _parse_classification_entry(self, element: ET.Element) -> Ssp1ClassificationEntry:
        return Ssp1ClassificationEntry(
            keyword=element.attrib["keyword"],
            text=element.text or "",
            type=element.attrib.get("type", "text/plain"),
            href=element.attrib.get(XLINK_HREF),
            linked_type=element.attrib.get("linkedType"),
            id=element.attrib.get("id"),
            description=element.attrib.get("description"),
            content=[clone_element(child) for child in element],
        )

    def _serialize_classification_entry(self, entry: Ssp1ClassificationEntry) -> ET.Element:
        element = ET.Element(qname(NS_STC, "ClassificationEntry"))
        element.set("keyword", entry.keyword)
        if entry.type != "text/plain":
            element.set("type", entry.type)
        self._set_link_attributes(element, href=entry.href, linked_type=entry.linked_type)
        if entry.id is not None:
            element.set("id", entry.id)
        if entry.description is not None:
            element.set("description", entry.description)
        if entry.text:
            element.text = entry.text
        for child in entry.content:
            element.append(clone_element(child))
        return element

    def _set_link_attributes(self, element: ET.Element, *, href: str | None, linked_type: str | None) -> None:
        if href is not None:
            element.set(XLINK_TYPE, "simple")
            element.set(XLINK_HREF, href)
        if linked_type is not None:
            element.set("linkedType", linked_type)

    def _render_xml(self, root: ET.Element) -> str:
        ET.register_namespace("srmd", NS_SRMD)
        ET.register_namespace("ssc", NS_SSC)
        ET.register_namespace("stc", NS_STC)
        ET.register_namespace("xlink", NS_XLINK)
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)
