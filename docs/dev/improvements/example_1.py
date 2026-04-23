"""Review example entry point.

Purpose:
- Demonstrate how the layered prototype is used end to end.
- Show altering existing items and adding new items through the domain API.

Boundary:
- Orchestrates the example only.
- Does not implement XML helpers, mappings, or domain definitions.
"""

from layer_example.document import CatalogDocument
from layer_example.domain import Book, Newspaper, Publisher
from layer_example.sample_data import XML_INPUT


def main() -> None:
    document = CatalogDocument.from_xml(XML_INPUT)
    catalog = document.catalog

    book = catalog.get_book("b1")
    newspaper = catalog.get_newspaper("n1")

    book.title = "Updated Title"
    book.year = "2024"
    book.edition = "2"
    book.publisher.city = "Stockholm"
    book.authors.append("Carol")

    newspaper.issue = "2026-04-23"
    newspaper.frequency = "daily"
    newspaper.publisher.city = "Metropolis"

    catalog.add_book(
        Book(
            book_id="b2",
            lang="sv",
            title="Schema by Example",
            authors=["Dana"],
            publisher=Publisher(name="Arc Light", city="Gothenburg"),
            year="2025",
            edition="1",
        )
    )
    catalog.add_newspaper(
        Newspaper(
            paper_id="n2",
            lang="sv",
            title="Morning Edition",
            publisher=Publisher(name="Nordic News", city="Malmo"),
            issue="2026-04-24",
            frequency="weekly",
        )
    )

    assert len(catalog.books) == 2
    assert len(catalog.newspapers) == 2

    print(document.to_xml())


if __name__ == "__main__":
    main()
