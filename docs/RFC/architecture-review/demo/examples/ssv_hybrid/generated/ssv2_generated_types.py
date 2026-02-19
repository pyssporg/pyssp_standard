from dataclasses import dataclass, field
from xml.etree import ElementTree as ET


NS_SSV = "http://ssp-standard.org/SSP1/SystemStructureParameterValues"


@dataclass
class GeneratedSsv2Value:
    type_name: str
    value: str


@dataclass
class GeneratedSsv2Parameter:
    name: str
    value: GeneratedSsv2Value


@dataclass
class GeneratedSsv2ParameterSet:
    name: str
    version: str
    parameters: list[GeneratedSsv2Parameter] = field(default_factory=list)


class GeneratedSsv2Codec:
    """Simulates xsdata-generated parse/serialize behavior for a tiny subset."""

    @staticmethod
    def parse(xml_text: str) -> GeneratedSsv2ParameterSet:
        root = ET.fromstring(xml_text)
        name = root.attrib.get("name", "unnamed")
        version = root.attrib.get("version", "2.0")

        params = []
        params_node = root.find(f"{{{NS_SSV}}}Parameters")
        if params_node is not None:
            for p in params_node.findall(f"{{{NS_SSV}}}Parameter"):
                p_name = p.attrib["name"]
                first = list(p)[0]
                type_name = first.tag.split("}", 1)[-1]
                value = first.attrib.get("value", "")
                params.append(GeneratedSsv2Parameter(name=p_name, value=GeneratedSsv2Value(type_name, value)))

        return GeneratedSsv2ParameterSet(name=name, version=version, parameters=params)

    @staticmethod
    def serialize(model: GeneratedSsv2ParameterSet) -> str:
        root = ET.Element(f"{{{NS_SSV}}}ParameterSet", attrib={"version": model.version, "name": model.name})
        root.set("xmlns:ssv", NS_SSV)
        params_node = ET.SubElement(root, f"{{{NS_SSV}}}Parameters")

        for p in model.parameters:
            p_node = ET.SubElement(params_node, f"{{{NS_SSV}}}Parameter", attrib={"name": p.name})
            ET.SubElement(p_node, f"{{{NS_SSV}}}{p.value.type_name}", attrib={"value": p.value.value})

        return ET.tostring(root, encoding="unicode")
