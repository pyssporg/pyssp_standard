from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping, Ssp1MappingEntry, Ssp1Transformation


NS_SSM = "http://ssp-standard.org/SSP1/SystemStructureParameterMapping"
NS_SSC = "http://ssp-standard.org/SSP1/SystemStructureCommon"


class Ssp1SsmXmlCodec:
    """Direct SSP1 SSM XML codec without generated bindings or archive logic."""

    def parse(self, xml_text: str) -> Ssp1ParameterMapping:
        root = ET.fromstring(xml_text)
        if root.tag != f"{{{NS_SSM}}}ParameterMapping":
            raise ValueError(f"Unexpected SSM root tag '{root.tag}'")

        document = Ssp1ParameterMapping(version=root.attrib.get("version", "1.0"))
        for child in list(root):
            if self._local_name(child.tag) != "MappingEntry":
                continue
            document.mappings.append(
                Ssp1MappingEntry(
                    source=child.attrib.get("source", ""),
                    target=child.attrib.get("target", ""),
                    suppress_unit_conversion=self._parse_bool(child.attrib.get("suppressUnitConversion")),
                    transformation=self._read_transformation(child),
                )
            )
        return document

    def serialize(self, document: Ssp1ParameterMapping) -> str:
        ET.register_namespace("ssm", NS_SSM)
        ET.register_namespace("ssc", NS_SSC)
        root = ET.Element(f"{{{NS_SSM}}}ParameterMapping", attrib={"version": document.version})
        for mapping in document.mappings:
            attrib = {"source": mapping.source, "target": mapping.target}
            if mapping.suppress_unit_conversion is not None:
                attrib["suppressUnitConversion"] = str(mapping.suppress_unit_conversion).lower()
            mapping_element = ET.SubElement(root, f"{{{NS_SSM}}}MappingEntry", attrib=attrib)
            if mapping.transformation is not None:
                ET.SubElement(
                    mapping_element,
                    f"{{{NS_SSC}}}{mapping.transformation.type_name}",
                    attrib=dict(mapping.transformation.attributes),
                )
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        return ET.tostring(root, encoding="unicode")

    def _read_transformation(self, mapping_entry: ET.Element) -> Ssp1Transformation | None:
        for child in list(mapping_entry):
            return Ssp1Transformation(
                type_name=self._local_name(child.tag),
                attributes=dict(child.attrib),
            )
        return None

    @staticmethod
    def _local_name(tag: str) -> str:
        return tag.split("}", 1)[-1]

    @staticmethod
    def _parse_bool(value: str | None) -> bool | None:
        if value is None:
            return None
        return value.lower() in {"true", "1"}
