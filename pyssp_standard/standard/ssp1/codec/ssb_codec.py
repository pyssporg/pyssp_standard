from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.codec.xml_utils import (
    NS_SSB,
    NS_SSC,
    append_annotations,
    append_enumerations,
    append_units,
    apply_metadata_attributes,
    find_type_child,
    first_child,
    local_name,
    parse_enumerations_container,
    parse_metadata_attributes,
    parse_units_container,
    qname,
    render_xml,
)
from pyssp_standard.standard.ssp1.model.ssb_model import Ssp1DictionaryEntry, Ssp1SignalDictionary


class Ssp1SsbCodec:
    def parse(self, xml_text: str) -> Ssp1SignalDictionary:
        root = ET.fromstring(xml_text)
        document = Ssp1SignalDictionary(
            version=root.attrib["version"],
            metadata=parse_metadata_attributes(root),
        )
        document.entries = [
            self._parse_entry(element)
            for element in root.findall(qname(NS_SSB, "DictionaryEntry"))
        ]
        document.enumerations = parse_enumerations_container(first_child(root, NS_SSB, "Enumerations"))
        document.units = parse_units_container(first_child(root, NS_SSB, "Units"))
        return document

    def serialize(self, document: Ssp1SignalDictionary) -> str:
        root = ET.Element(qname(NS_SSB, "SignalDictionary"))
        root.set("version", document.version)
        apply_metadata_attributes(root, document.metadata)
        for entry in document.entries:
            root.append(self._serialize_entry(entry))
        append_enumerations(root, document.enumerations, NS_SSB)
        append_units(root, document.units, NS_SSB)
        append_annotations(root, document.metadata.annotations, NS_SSB)
        return render_xml(root, {"ssc": NS_SSC, "ssb": NS_SSB})

    def _parse_entry(self, element: ET.Element) -> Ssp1DictionaryEntry:
        type_element = find_type_child(element, exclude_local_names={"Annotations"})
        if type_element is None:
            raise ValueError(f"DictionaryEntry '{element.attrib.get('name', '')}' is missing a typed value element")
        return Ssp1DictionaryEntry(
            name=element.attrib["name"],
            id=element.attrib.get("id"),
            description=element.attrib.get("description"),
            type_name=local_name(type_element.tag),
            attributes=dict(type_element.attrib),
            annotations=parse_metadata_attributes(element).annotations,
        )

    def _serialize_entry(self, entry: Ssp1DictionaryEntry) -> ET.Element:
        element = ET.Element(qname(NS_SSB, "DictionaryEntry"))
        element.set("name", entry.name)
        if entry.id is not None:
            element.set("id", entry.id)
        if entry.description is not None:
            element.set("description", entry.description)

        type_element = ET.SubElement(element, qname(NS_SSC, entry.type_name))
        for key, value in entry.attributes.items():
            type_element.set(key, str(value))

        append_annotations(element, entry.annotations, NS_SSB)
        return element
