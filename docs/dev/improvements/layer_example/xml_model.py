"""XML document layer.

Purpose:
- Hold XML names and generic ElementTree helpers.
- Encapsulate ordered insertion and readable serialization behavior.

Boundary:
- Knows XML structure mechanics, but not domain classes.
- Provides reusable low-level operations for higher layers.
- Does not decide how domain objects map to XML elements.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET


NS = "urn:books"
PREFIX = "bk"
CATALOG = f"{{{NS}}}catalog"
BOOK = f"{{{NS}}}book"
NEWSPAPER = f"{{{NS}}}newspaper"
TITLE = f"{{{NS}}}title"
AUTHOR = f"{{{NS}}}author"
YEAR = f"{{{NS}}}year"
PUBLISHER = f"{{{NS}}}publisher"
NAME = f"{{{NS}}}name"
CITY = f"{{{NS}}}city"
ISSUE = f"{{{NS}}}issue"


def parse_xml(xml_text: str) -> ET.Element:
    return ET.fromstring(xml_text)


def set_or_insert_attr(
    element: ET.Element,
    name: str,
    value: str,
    ordered_names: list[str],
) -> None:
    if name in element.attrib:
        element.attrib[name] = value
        return

    updated: dict[str, str] = {}
    inserted = False
    current = dict(element.attrib)

    for ordered_name in ordered_names:
        if ordered_name == name:
            updated[name] = value
            inserted = True
        if ordered_name in current:
            updated[ordered_name] = current[ordered_name]

    if not inserted:
        updated[name] = value

    for attr_name, attr_value in current.items():
        if attr_name not in updated:
            updated[attr_name] = attr_value

    element.attrib.clear()
    element.attrib.update(updated)


def replace_text_content(parent: ET.Element, child_name: str, value: str) -> None:
    child = parent.find(child_name)
    if child is None:
        child = ET.SubElement(parent, child_name)
    child.text = value


def insert_child_schema_ordered(
    parent: ET.Element,
    child: ET.Element,
    ordered_names: list[str],
) -> None:
    child_order = {name: index for index, name in enumerate(ordered_names)}
    new_index = child_order.get(child.tag, len(ordered_names))

    for index, existing in enumerate(list(parent)):
        existing_index = child_order.get(existing.tag, len(ordered_names))
        if existing_index > new_index:
            parent.insert(index, child)
            return

    parent.append(child)


def set_or_insert_singleton_child(
    parent: ET.Element,
    child_name: str,
    value: str,
    ordered_names: list[str],
) -> None:
    existing = parent.find(child_name)
    if existing is not None:
        existing.text = value
        return

    child = ET.Element(child_name)
    child.text = value
    insert_child_schema_ordered(parent, child, ordered_names)


def get_or_create_child(
    parent: ET.Element,
    child_name: str,
    ordered_names: list[str],
) -> ET.Element:
    existing = parent.find(child_name)
    if existing is not None:
        return existing

    child = ET.Element(child_name)
    insert_child_schema_ordered(parent, child, ordered_names)
    return child


def indent(element: ET.Element, level: int = 0) -> None:
    whitespace = "\n" + "  " * level
    child_whitespace = "\n" + "  " * (level + 1)

    if len(element):
        if not element.text or not element.text.strip():
            element.text = child_whitespace
        for child in element:
            indent(child, level + 1)
        if not element[-1].tail or not element[-1].tail.strip():
            element[-1].tail = whitespace
    if level and (not element.tail or not element.tail.strip()):
        element.tail = whitespace


def serialize(element: ET.Element) -> str:
    ET.register_namespace(PREFIX, NS)
    indent(element)
    return ET.tostring(element, encoding="unicode")
