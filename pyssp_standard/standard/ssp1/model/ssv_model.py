from __future__ import annotations

from dataclasses import dataclass, field

from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1Annotation, Ssp1BaseUnit, Ssp1DocumentMetadata, Ssp1Unit
from pyssp_standard.standard.unit_conversion import generate_base_unit


@dataclass
class Ssp1Parameter:
    name: str
    type_name: str
    attributes: dict[str, str] = field(default_factory=dict)
    id: str | None = None
    description: str | None = None
    annotations: list[Ssp1Annotation] = field(default_factory=list)


@dataclass
class Ssp1ParameterSet:
    name: str
    version: str
    metadata: Ssp1DocumentMetadata = field(default_factory=Ssp1DocumentMetadata)
    parameters: list[Ssp1Parameter] = field(default_factory=list)
    units: list[Ssp1Unit] = field(default_factory=list)

    def add_parameter(
        self,
        parname: str,
        ptype: str = "Real",
        *,
        value: float = None,
        name: str = None,
        mimetype: str | None = None,
        unit: str | None = None,
    ) -> Ssp1Parameter:
        attributes: dict[str, str] = {}
        if value is not None:
            attributes["value"] = str(value)
        if name is not None:
            attributes["name"] = name
        if mimetype is not None:
            attributes["mime-type"] = mimetype
        if unit is not None:
            attributes["unit"] = unit

        parameter = Ssp1Parameter(name=parname, type_name=ptype, attributes=attributes)
        self.parameters.append(parameter)
        return parameter

    def add_unit(self, name: str, base_unit: dict[str, object] | None = None) -> Ssp1Unit:
        if base_unit is None:
            base_unit = generate_base_unit(name)

        unit = Ssp1Unit(name=name, base_unit=Ssp1BaseUnit.from_dict(base_unit))
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

    def get_unit(self, name: str) -> Ssp1Unit | None:
        for unit in self.units:
            if unit.name == name:
                return unit
        return None
