from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from pyssp_standard.standard.ssp1.model.ssc_model import (
    Ssp1Annotation,
    Ssp1DocumentMetadata,
    Ssp1Enumeration,
    Ssp1EnumerationItem,
    Ssp1Unit,
)
from pyssp_standard.standard.ssp1.model.common_collections import (
    add_enumeration as add_common_enumeration,
    add_unit as add_common_unit,
    get_unit as get_common_unit,
)
from pyssp_standard.standard.common.utils import infer_parameter_type_name, merge_value_attribute


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
    enumerations: list[Ssp1Enumeration] = field(default_factory=list)
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

    def extend_parameters(
        self,
        parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object]],
    ) -> list[Ssp1Parameter]:
        """Append parameters from compact values or explicit parameters."""
        created: list[Ssp1Parameter] = []
        entries = parameters.items() if isinstance(parameters, Mapping) else parameters

        for entry in entries:
            if isinstance(entry, Ssp1Parameter):
                parameter = entry
            elif isinstance(entry, tuple):
                if len(entry) != 2:
                    raise ValueError(f"Parameter tuple entries must have exactly 2 items, got {len(entry)}")
                name, value = entry
                parameter = Ssp1Parameter(
                    name=str(name),
                    type_name=infer_parameter_type_name(value),
                    attributes=merge_value_attribute({}, value),
                )
            else:
                raise TypeError(f"Unsupported parameter entry: {entry!r}")
            self.parameters.append(parameter)
            created.append(parameter)

        return created

    def add_unit(self, name: str, base_unit: dict[str, object] | None = None) -> Ssp1Unit:
        return add_common_unit(self.units, name, base_unit)

    def get_unit(self, name: str) -> Ssp1Unit | None:
        return get_common_unit(self.units, name)

    def add_enumeration(self, name: str, items: list[Ssp1EnumerationItem]) -> Ssp1Enumeration:
        return add_common_enumeration(self.enumerations, name, items)
