from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1MappingEntry, Ssp1ParameterMapping
from pyssp_standard.standard.ssp1.codec.xml_utils import (
    NS_SSC,
    NS_SSM,
    append_annotations,
    append_transformation,
    apply_metadata_attributes,
    find_type_child,
    parse_bool,
    parse_metadata_attributes,
    parse_transformation,
    qname,
    render_xml,
)


class Ssp1SsmCodec:
    def parse(self, xml_text: str) -> Ssp1ParameterMapping:
        root = ET.fromstring(xml_text)
        document = Ssp1ParameterMapping(version=root.attrib["version"], metadata=parse_metadata_attributes(root))
        document.mappings = [self._parse_mapping_entry(element) for element in root.findall(qname(NS_SSM, "MappingEntry"))]
        return document

    def serialize(self, document: Ssp1ParameterMapping) -> str:
        root = ET.Element(qname(NS_SSM, "ParameterMapping"))
        root.set("version", document.version)
        apply_metadata_attributes(root, document.metadata)
        for mapping in document.mappings:
            root.append(self._serialize_mapping_entry(mapping))
        append_annotations(root, document.metadata.annotations, NS_SSM)
        return render_xml(root, {"ssc": NS_SSC, "ssm": NS_SSM})

    def _parse_mapping_entry(self, element: ET.Element) -> Ssp1MappingEntry:
        transformation_element = find_type_child(element, exclude_local_names={"Annotations"})
        return Ssp1MappingEntry(
            source=element.attrib["source"],
            target=element.attrib["target"],
            suppress_unit_conversion=parse_bool(element.attrib.get("suppressUnitConversion")),
            transformation=parse_transformation(transformation_element),
            id=element.attrib.get("id"),
            description=element.attrib.get("description"),
            annotations=parse_metadata_attributes(element).annotations,
        )

    def _serialize_mapping_entry(self, mapping: Ssp1MappingEntry) -> ET.Element:
        element = ET.Element(qname(NS_SSM, "MappingEntry"))
        element.set("source", mapping.source)
        element.set("target", mapping.target)
        if mapping.id is not None:
            element.set("id", mapping.id)
        if mapping.description is not None:
            element.set("description", mapping.description)
        if mapping.suppress_unit_conversion is not None:
            element.set("suppressUnitConversion", "true" if mapping.suppress_unit_conversion else "false")
        append_transformation(element, mapping.transformation)
        append_annotations(element, mapping.annotations, NS_SSM)
        return element
