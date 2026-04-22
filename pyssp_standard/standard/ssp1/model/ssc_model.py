from __future__ import annotations

from dataclasses import dataclass, field
from xml.etree import ElementTree as ET


@dataclass
class Ssp1Annotation:
    type_name: str
    elements: list[ET.Element] = field(default_factory=list)


@dataclass
class Ssp1DocumentMetadata:
    id: str | None = None
    description: str | None = None
    author: str | None = None
    fileversion: str | None = None
    copyright: str | None = None
    license: str | None = None
    generation_tool: str | None = None
    generation_date_and_time: str | None = None
    annotations: list[Ssp1Annotation] = field(default_factory=list)


@dataclass
class Ssp1BaseUnit:
    kg: int | None = None
    m: int | None = None
    s: int | None = None
    a: int | None = None
    k: int | None = None
    mol: int | None = None
    cd: int | None = None
    rad: int | None = None
    factor: float | None = None
    offset: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Ssp1BaseUnit":
        normalized: dict[str, object] = {}
        for key, value in data.items():
            target_key = key.lower() if key in {"A", "K"} else key
            if target_key in cls.__dataclass_fields__:
                normalized[target_key] = value
        return cls(**normalized)


@dataclass
class Ssp1Unit:
    name: str
    base_unit: Ssp1BaseUnit
    id: str | None = None
    description: str | None = None
    annotations: list[Ssp1Annotation] = field(default_factory=list)


@dataclass
class Ssp1EnumerationItem:
    name: str
    value: int


@dataclass
class Ssp1Enumeration:
    name: str
    items: list[Ssp1EnumerationItem] = field(default_factory=list)
    id: str | None = None
    description: str | None = None
    annotations: list[Ssp1Annotation] = field(default_factory=list)


@dataclass
class Ssp1Transformation:
    type_name: str
    attributes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.attributes = {key: str(value) for key, value in self.attributes.items()}
