from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Fmi2InterfaceAttributes:
    model_identifier: str
    can_get_and_set_fmu_state: bool = False
    can_serialize_fmu_state: bool = False
    provides_directional_derivative: bool = False
    needs_execution_tool: bool = False
    completed_integrator_step_not_needed: bool = False
    can_be_instantiated_only_once_per_process: bool = False
    can_not_use_memory_management_functions: bool = False
    extra_attributes: dict[str, str] = field(default_factory=dict)


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
    index: int
    dependencies: list[int] = field(default_factory=list)
    dependencies_kind: list[str] = field(default_factory=list)


@dataclass
class Fmi2ModelStructure:
    outputs: list[Fmi2Unknown] = field(default_factory=list)
    derivatives: list[Fmi2Unknown] = field(default_factory=list)
    initial_unknowns: list[Fmi2Unknown] = field(default_factory=list)


@dataclass
class Fmi2ScalarVariable:
    name: str
    value_reference: int
    type_name: str
    description: str | None = None
    causality: str | None = None
    variability: str | None = None
    initial: str | None = None
    declared_type: str | None = None
    start: str | float | int | None = None
    unit: str | None = None
    type_attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi2ModelDescriptionDocument:
    root: Fmi2ElementInfo
    fmi_version: str
    model_name: str
    guid: str
    description: str | None = None
    author: str | None = None
    version: str | None = None
    generation_tool: str | None = None
    generation_date_and_time: str | None = None
    variable_naming_convention: str | None = None
    number_of_event_indicators: int | None = None
    interface_type: str | None = None
    capabilities: Fmi2InterfaceAttributes | None = None
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

    def get_type_definitions(self, name: str | None = None, type_name: str | None = None) -> list[Fmi2TypeDefinition]:
        matches: list[Fmi2TypeDefinition] = []
        for definition in self.type_definitions:
            if name is not None and definition.name != name:
                continue
            if type_name is not None and definition.type_name != type_name:
                continue
            matches.append(definition)
        return matches

    def get_units(self, name: str | None = None) -> list[Fmi2Unit]:
        if name is None:
            return list(self.unit_definitions)
        return [unit for unit in self.unit_definitions if unit.name == name]

