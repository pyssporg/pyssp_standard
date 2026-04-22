from __future__ import annotations

from copy import deepcopy
from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model.ssc_model import (
    Ssp1Annotation,
    Ssp1BaseUnit,
    Ssp1DocumentMetadata,
    Ssp1Enumeration,
    Ssp1EnumerationItem,
    Ssp1Transformation,
    Ssp1Unit,
)


NS_SSC = "http://ssp-standard.org/SSP1/SystemStructureCommon"
NS_SSB = "http://ssp-standard.org/SSP1/SystemStructureSignalDictionary"
NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"
NS_SSM = "http://ssp-standard.org/SSP1/SystemStructureParameterMapping"
NS_SSV = "http://ssp-standard.org/SSP1/SystemStructureParameterValues"

XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'

METADATA_ATTRS = {
    "id": "id",
    "description": "description",
    "author": "author",
    "fileversion": "fileversion",
    "copyright": "copyright",
    "license": "license",
    "generation_tool": "generationTool",
    "generation_date_and_time": "generationDateAndTime",
}

BASE_UNIT_ATTRS = ("kg", "m", "s", "A", "K", "mol", "cd", "rad", "factor", "offset")


def qname(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def local_name(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def clone_element(element: ET.Element) -> ET.Element:
    return deepcopy(element)


def first_child(element: ET.Element, namespace: str, tag: str) -> ET.Element | None:
    return element.find(qname(namespace, tag))


def first_child_by_local_name(element: ET.Element, tag: str) -> ET.Element | None:
    for child in element:
        if local_name(child.tag) == tag:
            return child
    return None


def find_type_child(element: ET.Element, *, exclude_local_names: set[str] | None = None) -> ET.Element | None:
    excluded = exclude_local_names or set()
    for child in element:
        if local_name(child.tag) in excluded:
            continue
        return child
    return None


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    return float(value)


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == "true"


def bool_text(value: bool | None) -> str | None:
    if value is None:
        return None
    return "true" if value else "false"


def format_optional(value: object | None) -> str | None:
    if value is None:
        return None
    return str(value)


def normalize_binding_prefix(prefix: str | None) -> str | None:
    if prefix is None:
        return None
    return prefix[:-1] if prefix.endswith(".") else prefix


def serialize_binding_prefix(prefix: str | None) -> str | None:
    if prefix in (None, ""):
        return None
    return prefix if prefix.endswith(".") else f"{prefix}."


def apply_metadata_attributes(element: ET.Element, metadata: Ssp1DocumentMetadata) -> None:
    for field_name, attribute_name in METADATA_ATTRS.items():
        value = getattr(metadata, field_name)
        if value is not None:
            element.set(attribute_name, str(value))


def parse_metadata_attributes(element: ET.Element) -> Ssp1DocumentMetadata:
    metadata = Ssp1DocumentMetadata()
    for field_name, attribute_name in METADATA_ATTRS.items():
        setattr(metadata, field_name, element.attrib.get(attribute_name))
    metadata.annotations = parse_annotations_container(first_child_by_local_name(element, "Annotations"))
    return metadata


def parse_annotations_container(annotations_element: ET.Element | None) -> list[Ssp1Annotation]:
    if annotations_element is None:
        return []

    annotations: list[Ssp1Annotation] = []
    for annotation_element in annotations_element.findall(qname(NS_SSC, "Annotation")):
        annotations.append(
            Ssp1Annotation(
                type_name=annotation_element.attrib["type"],
                elements=[clone_element(child) for child in annotation_element],
            )
        )
    return annotations


def append_annotations(parent: ET.Element, annotations: list[Ssp1Annotation], container_namespace: str) -> None:
    if not annotations:
        return

    annotations_element = ET.SubElement(parent, qname(container_namespace, "Annotations"))
    for annotation in annotations:
        annotation_element = ET.SubElement(annotations_element, qname(NS_SSC, "Annotation"))
        annotation_element.set("type", annotation.type_name)
        for child in annotation.elements:
            annotation_element.append(clone_element(child))


def parse_units_container(units_element: ET.Element | None) -> list[Ssp1Unit]:
    if units_element is None:
        return []

    units: list[Ssp1Unit] = []
    for unit_element in units_element.findall(qname(NS_SSC, "Unit")):
        base_unit_element = first_child(unit_element, NS_SSC, "BaseUnit")
        base_unit_data = {
            ("a" if key == "A" else "k" if key == "K" else key): _parse_unit_value(value)
            for key, value in (base_unit_element.attrib.items() if base_unit_element is not None else [])
        }
        units.append(
            Ssp1Unit(
                name=unit_element.attrib["name"],
                id=unit_element.attrib.get("id"),
                description=unit_element.attrib.get("description"),
                base_unit=Ssp1BaseUnit.from_dict(base_unit_data),
                annotations=parse_annotations_container(first_child_by_local_name(unit_element, "Annotations")),
            )
        )
    return units


def append_units(parent: ET.Element, units: list[Ssp1Unit], container_namespace: str) -> None:
    if not units:
        return

    units_element = ET.SubElement(parent, qname(container_namespace, "Units"))
    for unit in units:
        unit_element = ET.SubElement(units_element, qname(NS_SSC, "Unit"))
        if unit.id is not None:
            unit_element.set("id", unit.id)
        if unit.description is not None:
            unit_element.set("description", unit.description)
        unit_element.set("name", unit.name)

        base_unit_element = ET.SubElement(unit_element, qname(NS_SSC, "BaseUnit"))
        for attribute_name in BASE_UNIT_ATTRS:
            field_name = "a" if attribute_name == "A" else "k" if attribute_name == "K" else attribute_name
            value = getattr(unit.base_unit, field_name)
            if value is not None:
                base_unit_element.set(attribute_name, str(value))

        append_annotations(unit_element, unit.annotations, NS_SSC)


def parse_enumerations_container(enumerations_element: ET.Element | None) -> list[Ssp1Enumeration]:
    if enumerations_element is None:
        return []

    enumerations: list[Ssp1Enumeration] = []
    for enumeration_element in enumerations_element.findall(qname(NS_SSC, "Enumeration")):
        enumerations.append(
            Ssp1Enumeration(
                name=enumeration_element.attrib["name"],
                id=enumeration_element.attrib.get("id"),
                description=enumeration_element.attrib.get("description"),
                items=[
                    Ssp1EnumerationItem(
                        name=item.attrib["name"],
                        value=int(item.attrib["value"]),
                    )
                    for item in enumeration_element.findall(qname(NS_SSC, "Item"))
                ],
                annotations=parse_annotations_container(first_child_by_local_name(enumeration_element, "Annotations")),
            )
        )
    return enumerations


def append_enumerations(parent: ET.Element, enumerations: list[Ssp1Enumeration], container_namespace: str) -> None:
    if not enumerations:
        return

    enumerations_element = ET.SubElement(parent, qname(container_namespace, "Enumerations"))
    for enumeration in enumerations:
        enumeration_element = ET.SubElement(enumerations_element, qname(NS_SSC, "Enumeration"))
        enumeration_element.set("name", enumeration.name)
        if enumeration.id is not None:
            enumeration_element.set("id", enumeration.id)
        if enumeration.description is not None:
            enumeration_element.set("description", enumeration.description)
        for item in enumeration.items:
            item_element = ET.SubElement(enumeration_element, qname(NS_SSC, "Item"))
            item_element.set("name", item.name)
            item_element.set("value", str(item.value))
        append_annotations(enumeration_element, enumeration.annotations, NS_SSC)


def parse_transformation(element: ET.Element | None) -> Ssp1Transformation | None:
    if element is None:
        return None
    return Ssp1Transformation(type_name=local_name(element.tag), attributes=dict(element.attrib))


def append_transformation(parent: ET.Element, transformation: Ssp1Transformation | None) -> None:
    if transformation is None:
        return
    transformation_element = ET.SubElement(parent, qname(NS_SSC, transformation.type_name))
    for key, value in transformation.attributes.items():
        transformation_element.set(key, str(value))


def render_xml(root: ET.Element, namespace_map: dict[str, str]) -> str:
    for prefix, namespace in namespace_map.items():
        ET.register_namespace(prefix, namespace)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def _parse_unit_value(value: str) -> int | float:
    if any(marker in value for marker in (".", "e", "E")):
        return float(value)
    return int(value)
