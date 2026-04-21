from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Fmi2ElementInfo:
    tag: str
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi2DefaultExperiment:
    start_time: float | None = None
    stop_time: float | None = None
    tolerance: float | None = None


@dataclass
class Fmi2Unit:
    name: str
    base_unit: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi2TypeDefinition:
    name: str
    type_name: str
    attributes: dict[str, str] = field(default_factory=dict)
    enumeration_items: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Fmi2Unknown:
    index: str
    dependencies: str | None = None
    dependencies_kind: str | None = None


@dataclass
class Fmi2ModelStructure:
    outputs: list[Fmi2Unknown] = field(default_factory=list)
    derivatives: list[Fmi2Unknown] = field(default_factory=list)
    initial_unknowns: list[Fmi2Unknown] = field(default_factory=list)


@dataclass
class Fmi2ScalarVariable:
    name: str
    value_reference: str
    type_name: str
    description: str | None = None
    causality: str | None = None
    variability: str | None = None
    initial: str | None = None
    declared_type: str | None = None
    start: str | None = None
    type_attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi2ModelDescriptionDocument:
    root: Fmi2ElementInfo
    fmi_version: str
    model_name: str
    guid: str
    generation_tool: str | None = None
    generation_date_and_time: str | None = None
    variable_naming_convention: str | None = None
    number_of_event_indicators: int | None = None
    interface_type: str | None = None
    interface_attributes: dict[str, str] = field(default_factory=dict)
    unit_definitions: list[Fmi2Unit] = field(default_factory=list)
    type_definitions: list[Fmi2TypeDefinition] = field(default_factory=list)
    variables: list[Fmi2ScalarVariable] = field(default_factory=list)
    model_structure: Fmi2ModelStructure = field(default_factory=Fmi2ModelStructure)
    default_experiment: Fmi2DefaultExperiment | None = None

    def get(
        self,
        causality: str | None = None,
        variability: str | None = None,
    ) -> list[Fmi2ScalarVariable]:
        matches: list[Fmi2ScalarVariable] = []
        for variable in self.variables:
            if causality is not None and variable.causality != causality:
                continue
            if variability is not None and variable.variability != variability:
                continue
            matches.append(variable)
        return matches

    @property
    def inputs(self) -> list[Fmi2ScalarVariable]:
        return self.get(causality="input")

    @property
    def outputs(self) -> list[Fmi2ScalarVariable]:
        return self.get(causality="output")

    @property
    def parameters(self) -> list[Fmi2ScalarVariable]:
        return self.get(causality="parameter")
