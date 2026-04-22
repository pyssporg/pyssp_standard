from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter
from pyssp_standard.standard.ssp1.codec.xml_utils import (
    NS_SSV,
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


class Ssp1SsvCodec:
    def parse(self, xml_text: str) -> Ssp1ParameterSet:
        root = ET.fromstring(xml_text)
        document = Ssp1ParameterSet(
            name=root.attrib["name"],
            version=root.attrib["version"],
            metadata=parse_metadata_attributes(root),
        )
        parameters_element = first_child(root, NS_SSV, "Parameters")
        if parameters_element is not None:
            document.parameters = [
                self._parse_parameter(element)
                for element in parameters_element.findall(qname(NS_SSV, "Parameter"))
            ]
        document.enumerations = parse_enumerations_container(first_child(root, NS_SSV, "Enumerations"))
        document.units = parse_units_container(first_child(root, NS_SSV, "Units"))
        return document

    def serialize(self, model: Ssp1ParameterSet) -> str:
        root = ET.Element(qname(NS_SSV, "ParameterSet"))
        root.set("version", model.version)
        root.set("name", model.name)
        apply_metadata_attributes(root, model.metadata)

        parameters_element = ET.SubElement(root, qname(NS_SSV, "Parameters"))
        for parameter in model.parameters:
            parameters_element.append(self._serialize_parameter(parameter))

        append_enumerations(root, model.enumerations, NS_SSV)
        append_units(root, model.units, NS_SSV)
        append_annotations(root, model.metadata.annotations, NS_SSV)
        return render_xml(root, {"ssv": NS_SSV})

    def _parse_parameter(self, element: ET.Element) -> Ssp1Parameter:
        type_element = find_type_child(element, exclude_local_names={"Annotations"})
        if type_element is None:
            raise ValueError(f"Parameter '{element.attrib.get('name', '')}' is missing a typed value element")
        return Ssp1Parameter(
            name=element.attrib["name"],
            id=element.attrib.get("id"),
            description=element.attrib.get("description"),
            type_name=local_name(type_element.tag),
            attributes=dict(type_element.attrib),
            annotations=parse_metadata_attributes(element).annotations,
        )

    def _serialize_parameter(self, parameter: Ssp1Parameter) -> ET.Element:
        element = ET.Element(qname(NS_SSV, "Parameter"))
        element.set("name", parameter.name)
        if parameter.id is not None:
            element.set("id", parameter.id)
        if parameter.description is not None:
            element.set("description", parameter.description)

        type_element = ET.SubElement(element, qname(NS_SSV, parameter.type_name))
        for key, value in parameter.attributes.items():
            if parameter.type_name == "Boolean" and key == "value":
                type_element.set(key, str(value).lower())
            else:
                type_element.set(key, str(value))

        append_annotations(element, parameter.annotations, NS_SSV)
        return element


class Ssp1SsvXsdataCodec(Ssp1SsvCodec):
    pass
