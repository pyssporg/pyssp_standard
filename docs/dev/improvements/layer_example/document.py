"""Document orchestration layer.

Purpose:
- Bind a parsed XML document to a domain aggregate.
- Own bindings between domain models and XML elements.
- Synchronize domain state back into XML for serialization.

Boundary:
- Knows the XML root and the mapping bindings.
- Exposes the bound domain aggregate but does not own domain behavior.
- Does not contain specialized field mapping logic; that stays in projection.py.
"""

from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET

from layer_example.domain import Book, Catalog, Newspaper
from layer_example.projection import (
    apply_book,
    apply_newspaper,
    make_book_element,
    make_newspaper_element,
    read_book,
    read_newspaper,
)
from layer_example.xml_model import (
    BOOK,
    NEWSPAPER,
    insert_child_schema_ordered,
    parse_xml,
    serialize,
)


@dataclass
class BookBinding:
    model: Book
    element: ET.Element

    def apply(self) -> None:
        apply_book(self.model, self.element)


@dataclass
class NewspaperBinding:
    model: Newspaper
    element: ET.Element

    def apply(self) -> None:
        apply_newspaper(self.model, self.element)


class CatalogDocument:
    def __init__(
        self,
        root: ET.Element,
        catalog: Catalog,
        book_bindings: list[BookBinding],
        newspaper_bindings: list[NewspaperBinding],
    ) -> None:
        self.root = root
        self.catalog = catalog
        self._book_bindings = book_bindings
        self._newspaper_bindings = newspaper_bindings

    @classmethod
    def from_xml(cls, xml_text: str) -> "CatalogDocument":
        root = parse_xml(xml_text)
        book_bindings = [
            BookBinding(model=read_book(element), element=element)
            for element in root.findall(BOOK)
        ]
        newspaper_bindings = [
            NewspaperBinding(model=read_newspaper(element), element=element)
            for element in root.findall(NEWSPAPER)
        ]
        catalog = Catalog(
            books=[binding.model for binding in book_bindings],
            newspapers=[binding.model for binding in newspaper_bindings],
        )
        return cls(
            root=root,
            catalog=catalog,
            book_bindings=book_bindings,
            newspaper_bindings=newspaper_bindings,
        )

    def _bind_book(self, book: Book) -> None:
        element = make_book_element()
        insert_child_schema_ordered(self.root, element, [BOOK, NEWSPAPER])
        binding = BookBinding(model=book, element=element)
        self._book_bindings.append(binding)

    def _bind_newspaper(self, newspaper: Newspaper) -> None:
        element = make_newspaper_element()
        insert_child_schema_ordered(self.root, element, [BOOK, NEWSPAPER])
        binding = NewspaperBinding(model=newspaper, element=element)
        self._newspaper_bindings.append(binding)

    def _sync_bindings(self) -> None:
        bound_books = {id(binding.model) for binding in self._book_bindings}
        for book in self.catalog.books:
            if id(book) not in bound_books:
                self._bind_book(book)

        bound_newspapers = {id(binding.model) for binding in self._newspaper_bindings}
        for newspaper in self.catalog.newspapers:
            if id(newspaper) not in bound_newspapers:
                self._bind_newspaper(newspaper)

    def apply(self) -> None:
        self._sync_bindings()
        for book in self._book_bindings:
            book.apply()
        for newspaper in self._newspaper_bindings:
            newspaper.apply()

    def to_xml(self) -> str:
        self.apply()
        return serialize(self.root)
