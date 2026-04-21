from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Ssp1Transformation:
    type_name: str
    attributes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.attributes = {key: str(value) for key, value in self.attributes.items()}


@dataclass
class Ssp1MappingEntry:
    source: str
    target: str
    suppress_unit_conversion: bool | None = None
    transformation: Ssp1Transformation | None = None


@dataclass
class Ssp1ParameterMapping:
    version: str
    mappings: list[Ssp1MappingEntry] = field(default_factory=list)

    def add_mapping(
        self,
        source: str,
        target: str,
        *,
        suppress_unit_conversion: bool | None = None,
        transformation: Ssp1Transformation | None = None,
    ) -> Ssp1MappingEntry:
        mapping = Ssp1MappingEntry(
            source=source,
            target=target,
            suppress_unit_conversion=suppress_unit_conversion,
            transformation=transformation,
        )
        self.mappings.append(mapping)
        return mapping

    def edit_mapping(
        self,
        *,
        target: str,
        source: str | None = None,
        suppress_unit_conversion: bool | None = None,
        transformation: Ssp1Transformation | None = None,
    ) -> Ssp1MappingEntry:
        for mapping in self.mappings:
            if mapping.target != target:
                continue
            if source is not None:
                mapping.source = source
            if suppress_unit_conversion is not None:
                mapping.suppress_unit_conversion = suppress_unit_conversion
            if transformation is not None:
                mapping.transformation = transformation
            return mapping
        raise KeyError(f"Mapping target '{target}' not found")
