from __future__ import annotations

from dataclasses import dataclass, field

from pyssp_standard.unit_conversion import generate_base_unit


@dataclass
class SsvDocumentMetadata:
    id: str | None = None
    description: str | None = None
    author: str | None = None
    fileversion: str | None = None
    copyright: str | None = None
    license: str | None = None
    generation_tool: str | None = None
    generation_date_and_time: str | None = None

    @property
    def generationTool(self) -> str | None:
        return self.generation_tool

    @generationTool.setter
    def generationTool(self, value: str | None) -> None:
        self.generation_tool = value

    @property
    def generationDateAndTime(self) -> str | None:
        return self.generation_date_and_time

    @generationDateAndTime.setter
    def generationDateAndTime(self, value: str | None) -> None:
        self.generation_date_and_time = value


@dataclass
class SsvBaseUnit:
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
    def from_dict(cls, base_unit: dict[str, object]) -> SsvBaseUnit:
        int_fields = {"kg", "m", "s", "A", "K", "mol", "cd", "rad"}
        float_fields = {"factor", "offset"}
        values: dict[str, int | float] = {}
        for key, value in base_unit.items():
            if value is None:
                continue
            mapped_key = {"A": "a", "K": "k"}.get(key, key)
            if mapped_key in {"kg", "m", "s", "a", "k", "mol", "cd", "rad"}:
                values[mapped_key] = int(value) if key in int_fields or mapped_key in {"a", "k"} else int(value)
            elif mapped_key in float_fields:
                values[mapped_key] = float(value)
        return cls(**values)


@dataclass
class SsvUnit:
    name: str
    base_unit: SsvBaseUnit
    id: str | None = None
    description: str | None = None


@dataclass
class SsvParameter:
    name: str
    type_name: str
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class SsvParameterSet:
    name: str
    version: str
    metadata: SsvDocumentMetadata = field(default_factory=SsvDocumentMetadata)
    parameters: list[SsvParameter] = field(default_factory=list)
    units: list[SsvUnit] = field(default_factory=list)

    def add_parameter(
        self,
        parname: str,
        ptype: str = "Real",
        *,
        value: float = None,
        name: str = None,
        mimetype: str | None = None,
        unit: str | None = None,
    ) -> SsvParameter:
        attributes: dict[str, str] = {}
        if value is not None:
            attributes["value"] = str(value)
        if name is not None:
            attributes["name"] = name
        if mimetype is not None:
            attributes["mime-type"] = mimetype
        if unit is not None:
            attributes["unit"] = unit

        parameter = SsvParameter(name=parname, type_name=ptype, attributes=attributes)
        self.parameters.append(parameter)
        return parameter

    def add_unit(self, name: str, base_unit: dict[str, object] | None = None) -> SsvUnit:
        if base_unit is None:
            base_unit = generate_base_unit(name)

        unit = SsvUnit(name=name, base_unit=SsvBaseUnit.from_dict(base_unit))
        existing = self.get_unit(name)
        if existing is None:
            self.units.append(unit)
            return unit

        if (
            existing.base_unit is not None
            and unit.base_unit is not None
            and existing.base_unit != unit.base_unit
        ):
            raise ValueError(f"Unit {name} already exists with different definition")

        if existing.base_unit is None:
            existing.base_unit = unit.base_unit
        return existing

    def get_unit(self, name: str) -> SsvUnit | None:
        for unit in self.units:
            if unit.name == name:
                return unit
        return None
