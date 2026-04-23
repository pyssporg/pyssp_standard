"""Domain layer.

Purpose:
- Define application-facing types without XML dependencies.
- Express the business shape of the data, including the catalog aggregate.

Boundary:
- No ElementTree usage.
- No parsing, serialization, or XML ordering logic.
- No knowledge of how models are bound back to document nodes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Publisher:
    name: str
    city: str | None = None


@dataclass
class Book:
    book_id: str
    lang: str
    title: str
    authors: list[str]
    publisher: Publisher
    year: str | None = None
    edition: str | None = None


@dataclass
class Newspaper:
    paper_id: str
    lang: str
    title: str
    publisher: Publisher
    issue: str | None = None
    frequency: str | None = None


@dataclass
class Catalog:
    books: list[Book]
    newspapers: list[Newspaper]

    def get_book(self, book_id: str) -> Book:
        for book in self.books:
            if book.book_id == book_id:
                return book
        raise KeyError(f"Unknown book id: {book_id}")

    def get_newspaper(self, paper_id: str) -> Newspaper:
        for newspaper in self.newspapers:
            if newspaper.paper_id == paper_id:
                return newspaper
        raise KeyError(f"Unknown newspaper id: {paper_id}")

    def add_book(self, book: Book) -> Book:
        self.books.append(book)
        return book

    def add_newspaper(self, newspaper: Newspaper) -> Newspaper:
        self.newspapers.append(newspaper)
        return newspaper
