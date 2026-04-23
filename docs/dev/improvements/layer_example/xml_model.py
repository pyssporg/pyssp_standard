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

from collections.abc import Callable
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


def remove_attr(element: ET.Element, name: str) -> None:
    element.attrib.pop(name, None)


def sync_optional_attr(
    element: ET.Element,
    name: str,
    value: str | None,
    ordered_names: list[str],
) -> None:
    if value is None:
        remove_attr(element, name)
        return
    set_or_insert_attr(element, name, value, ordered_names)


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


def remove_child(parent: ET.Element, child_name: str) -> None:
    existing = parent.find(child_name)
    if existing is not None:
        parent.remove(existing)


def sync_optional_singleton_child(
    parent: ET.Element,
    child_name: str,
    value: str | None,
    ordered_names: list[str],
) -> None:
    if value is None:
        remove_child(parent, child_name)
        return
    set_or_insert_singleton_child(parent, child_name, value, ordered_names)


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


def sync_nested_child(
    parent: ET.Element,
    child_name: str,
    model: object,
    ordered_names: list[str],
    apply_child: Callable[[object, ET.Element], None],
) -> ET.Element:
    child = get_or_create_child(parent, child_name, ordered_names)
    apply_child(model, child)
    return child


def sync_repeated_text_children(
    parent: ET.Element,
    child_name: str,
    values: list[str],
    ordered_names: list[str],
) -> None:
    existing_children = list(parent.findall(child_name))

    for child in existing_children:
        parent.remove(child)

    for value in values:
        child = ET.Element(child_name)
        child.text = value
        insert_child_schema_ordered(parent, child, ordered_names)


def sync_keyed_children(
    parent: ET.Element,
    items: list[object],
    child_name: str,
    ordered_names: list[str],
    get_item_key: Callable[[object], str],
    get_element_key: Callable[[ET.Element], str | None],
    make_child: Callable[[], ET.Element],
    apply_child: Callable[[object, ET.Element], None],
) -> None:
    existing_children = {
        get_element_key(element): element for element in parent.findall(child_name)
    }
    item_keys = {get_item_key(item) for item in items}

    for key, element in existing_children.items():
        if key is not None and key not in item_keys:
            parent.remove(element)

    for item in items:
        key = get_item_key(item)
        element = existing_children.get(key)
        if element is None:
            element = make_child()
            insert_child_schema_ordered(parent, element, ordered_names)
        apply_child(item, element)


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
