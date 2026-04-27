from __future__ import annotations

from pyssp_standard.standard.ssp1.model.ssc_model import (
    Ssp1BaseUnit,
    Ssp1Enumeration,
    Ssp1EnumerationItem,
    Ssp1Unit,
)
from pyssp_standard.standard.unit_conversion import generate_base_unit


def get_unit(units: list[Ssp1Unit], name: str) -> Ssp1Unit | None:
    for unit in units:
        if unit.name == name:
            return unit
    return None


def add_unit(
    units: list[Ssp1Unit],
    name: str,
    base_unit: dict[str, object] | None = None,
) -> Ssp1Unit:
    if base_unit is None:
        base_unit = generate_base_unit(name)

    unit = Ssp1Unit(name=name, base_unit=Ssp1BaseUnit.from_dict(base_unit))
    existing = get_unit(units, name)
    if existing is None:
        units.append(unit)
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


def add_enumeration(
    enumerations: list[Ssp1Enumeration],
    name: str,
    items: list[Ssp1EnumerationItem],
) -> Ssp1Enumeration:
    enumeration = Ssp1Enumeration(name=name, items=list(items))
    enumerations.append(enumeration)
    return enumeration
