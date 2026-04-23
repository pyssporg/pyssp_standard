"""Projection layer.

Purpose:
- Translate between domain objects and XML elements.
- Keep specialized mapping rules close to the relevant domain types.

Boundary:
- Knows both domain models and XML helper functions.
- Contains read/apply logic, but not document ownership or catalog orchestration.
- Avoids direct user-facing document APIs.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from layer_example.domain import Book, Newspaper, Publisher
from layer_example.xml_model import (
    AUTHOR,
    BOOK,
    CITY,
    ISSUE,
    NAME,
    NEWSPAPER,
    PUBLISHER,
    TITLE,
    YEAR,
    get_or_create_child,
    insert_child_schema_ordered,
    replace_text_content,
    set_or_insert_attr,
    set_or_insert_singleton_child,
)


def read_publisher(element: ET.Element) -> Publisher:
    return Publisher(
        name=element.findtext(NAME, default=""),
        city=element.findtext(CITY),
    )


def read_book(element: ET.Element) -> Book:
    return Book(
        book_id=element.attrib["id"],
        lang=element.attrib["lang"],
        title=element.findtext(TITLE, default=""),
        authors=[child.text or "" for child in element.findall(AUTHOR)],
        publisher=read_publisher(element.find(PUBLISHER) or ET.Element(PUBLISHER)),
        year=element.findtext(YEAR),
        edition=element.attrib.get("edition"),
    )


def read_newspaper(element: ET.Element) -> Newspaper:
    return Newspaper(
        paper_id=element.attrib["id"],
        lang=element.attrib["lang"],
        title=element.findtext(TITLE, default=""),
        publisher=read_publisher(element.find(PUBLISHER) or ET.Element(PUBLISHER)),
        issue=element.findtext(ISSUE),
        frequency=element.attrib.get("frequency"),
    )


def apply_publisher(
    publisher: Publisher,
    element: ET.Element,
    ordered_names: list[str],
) -> None:
    replace_text_content(element, NAME, publisher.name)
    if publisher.city is not None:
        set_or_insert_singleton_child(element, CITY, publisher.city, ordered_names)

# TODO: Generic xml_model?
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

# TODO: CAn parts here be moved to the generic xml model?
def apply_book(book: Book, element: ET.Element) -> None:
    attr_order = ["id", "lang", "edition"]
    child_order = [TITLE, AUTHOR, PUBLISHER, YEAR]
    publisher_child_order = [NAME, CITY]

    set_or_insert_attr(element, "id", book.book_id, attr_order)
    set_or_insert_attr(element, "lang", book.lang, attr_order)
    if book.edition is not None:
        set_or_insert_attr(element, "edition", book.edition, attr_order)

    replace_text_content(element, TITLE, book.title)
    sync_repeated_text_children(element, AUTHOR, book.authors, child_order)
    publisher_element = get_or_create_child(element, PUBLISHER, child_order)
    apply_publisher(book.publisher, publisher_element, publisher_child_order)

    if book.year is not None:
        set_or_insert_singleton_child(element, YEAR, book.year, child_order)


def apply_newspaper(newspaper: Newspaper, element: ET.Element) -> None:
    attr_order = ["id", "lang", "frequency"]
    child_order = [TITLE, PUBLISHER, ISSUE]
    publisher_child_order = [NAME, CITY]

    set_or_insert_attr(element, "id", newspaper.paper_id, attr_order)
    set_or_insert_attr(element, "lang", newspaper.lang, attr_order)
    if newspaper.frequency is not None:
        set_or_insert_attr(element, "frequency", newspaper.frequency, attr_order)

    replace_text_content(element, TITLE, newspaper.title)
    publisher_element = get_or_create_child(element, PUBLISHER, child_order)
    apply_publisher(newspaper.publisher, publisher_element, publisher_child_order)

    if newspaper.issue is not None:
        set_or_insert_singleton_child(element, ISSUE, newspaper.issue, child_order)


def make_book_element() -> ET.Element:
    return ET.Element(BOOK)


def make_newspaper_element() -> ET.Element:
    return ET.Element(NEWSPAPER)
