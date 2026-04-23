"""Projection layer.

Purpose:
- Translate between domain objects and XML elements.
- Keep specialized mapping rules close to the relevant domain types.

Boundary:
- Knows both domain models and XML helper functions.
- Contains read/apply logic, including aggregate-level translation.
- Avoids direct user-facing document APIs.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from layer_example.domain import Book, Catalog, Newspaper, Publisher
from layer_example.xml_model import (
    AUTHOR,
    BOOK,
    CATALOG,
    CITY,
    ISSUE,
    NAME,
    NEWSPAPER,
    PUBLISHER,
    TITLE,
    YEAR,
    replace_text_content,
    sync_keyed_children,
    sync_nested_child,
    sync_optional_attr,
    sync_optional_singleton_child,
    sync_repeated_text_children,
)


def read_publisher(element: ET.Element) -> Publisher:
    return Publisher(
        name=element.findtext(NAME, default=""),
        city=element.findtext(CITY),
    )


def read_catalog(root: ET.Element) -> Catalog:
    return Catalog(
        books=[read_book(element) for element in root.findall(BOOK)],
        newspapers=[read_newspaper(element) for element in root.findall(NEWSPAPER)],
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
    sync_optional_singleton_child(element, CITY, publisher.city, ordered_names)


def apply_book(book: Book, element: ET.Element) -> None:
    attr_order = ["id", "lang", "edition"]
    child_order = [TITLE, AUTHOR, PUBLISHER, YEAR]

    sync_optional_attr(element, "id", book.book_id, attr_order)
    sync_optional_attr(element, "lang", book.lang, attr_order)
    sync_optional_attr(element, "edition", book.edition, attr_order)
    replace_text_content(element, TITLE, book.title)
    sync_repeated_text_children(element, AUTHOR, book.authors, child_order)
    sync_nested_child(
        element,
        PUBLISHER,
        book.publisher,
        child_order,
        lambda model, child: apply_publisher(model, child, [NAME, CITY]),
    )
    sync_optional_singleton_child(element, YEAR, book.year, child_order)


def apply_newspaper(newspaper: Newspaper, element: ET.Element) -> None:
    attr_order = ["id", "lang", "frequency"]
    child_order = [TITLE, PUBLISHER, ISSUE]

    sync_optional_attr(element, "id", newspaper.paper_id, attr_order)
    sync_optional_attr(element, "lang", newspaper.lang, attr_order)
    sync_optional_attr(element, "frequency", newspaper.frequency, attr_order)
    replace_text_content(element, TITLE, newspaper.title)
    sync_nested_child(
        element,
        PUBLISHER,
        newspaper.publisher,
        child_order,
        lambda model, child: apply_publisher(model, child, [NAME, CITY]),
    )
    sync_optional_singleton_child(element, ISSUE, newspaper.issue, child_order)


def make_book_element() -> ET.Element:
    return ET.Element(BOOK)


def make_newspaper_element() -> ET.Element:
    return ET.Element(NEWSPAPER)


def publish_catalog(catalog: Catalog, root: ET.Element) -> None:
    if root.tag != CATALOG:
        raise ValueError(f"Expected catalog root, got: {root.tag}")

    sync_keyed_children(
        root,
        catalog.books,
        BOOK,
        [BOOK, NEWSPAPER],
        get_item_key=lambda model: model.book_id,
        get_element_key=lambda element: element.attrib.get("id"),
        make_child=make_book_element,
        apply_child=apply_book,
    )
    sync_keyed_children(
        root,
        catalog.newspapers,
        NEWSPAPER,
        [BOOK, NEWSPAPER],
        get_item_key=lambda model: model.paper_id,
        get_element_key=lambda element: element.attrib.get("id"),
        make_child=make_newspaper_element,
        apply_child=apply_newspaper,
    )
