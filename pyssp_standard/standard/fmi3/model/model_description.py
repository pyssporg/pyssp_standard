from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Fmi3ElementInfo:
    tag: str
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi3DefaultExperiment:
    start_time: float | None = None
    stop_time: float | None = None
    tolerance: float | None = None
    step_size: float | None = None


@dataclass
class Fmi3Unit:
    name: str
    base_unit: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi3TypeDefinition:
    name: str
    type_name: str
    attributes: dict[str, str] = field(default_factory=dict)
    enumeration_items: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Fmi3Unknown:
    value_reference: int
    dependencies: list[int] = field(default_factory=list)
    dependencies_kind: list[str] = field(default_factory=list)


@dataclass
class Fmi3ModelStructure:
    outputs: list[Fmi3Unknown] = field(default_factory=list)
    continuous_state_derivatives: list[Fmi3Unknown] = field(default_factory=list)
    clocked_states: list[Fmi3Unknown] = field(default_factory=list)
    initial_unknowns: list[Fmi3Unknown] = field(default_factory=list)
    event_indicators: list[Fmi3Unknown] = field(default_factory=list)


@dataclass
class Fmi3ScalarVariable:
    name: str
    value_reference: int
    type_name: str
    description: str | None = None
    causality: str | None = None
    variability: str | None = None
    initial: str | None = None
    declared_type: str | None = None
    start: str | None = None
    type_attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi3InterfaceAttributes:
    model_identifier: str
    needs_execution_tool: bool = False
    can_be_instantiated_only_once_per_process: bool = False
    can_get_and_set_fmu_state: bool = False
    can_serialize_fmu_state: bool = False
    provides_directional_derivatives: bool = False
    provides_adjoint_derivatives: bool = False
    provides_per_element_dependencies: bool = False
    extra_attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Fmi3ModelExchange(Fmi3InterfaceAttributes):
    needs_completed_integrator_step: bool = False
    provides_evaluate_discrete_states: bool = False


@dataclass
class Fmi3CoSimulation(Fmi3InterfaceAttributes):
    can_handle_variable_communication_step_size: bool = False
    fixed_internal_step_size: float | None = None
    max_output_derivative_order: int = 0
    recommended_intermediate_input_smoothness: int = 0
    provides_intermediate_update: bool = False
    might_return_early_from_do_step: bool = False
    can_return_early_after_intermediate_update: bool = False
    has_event_mode: bool = False
    provides_evaluate_discrete_states: bool = False


@dataclass
class Fmi3ScheduledExecution(Fmi3InterfaceAttributes):
    pass


@dataclass
class Fmi3ModelDescriptionDocument:
    root: Fmi3ElementInfo | None
    fmi_version: str
    model_name: str
    instantiation_token: str
    description: str | None = None
    author: str | None = None
    version: str | None = None
    copyright: str | None = None
    license: str | None = None
    generation_tool: str | None = None
    generation_date_and_time: str | None = None
    variable_naming_convention: str | None = None
    unit_definitions: list[Fmi3Unit] = field(default_factory=list)
    type_definitions: list[Fmi3TypeDefinition] = field(default_factory=list)
    variables: list[Fmi3ScalarVariable] = field(default_factory=list)
    model_structure: Fmi3ModelStructure = field(default_factory=Fmi3ModelStructure)
    default_experiment: Fmi3DefaultExperiment | None = None
    model_exchange: Fmi3ModelExchange | None = None
    co_simulation: Fmi3CoSimulation | None = None
    scheduled_execution: Fmi3ScheduledExecution | None = None

    def get(
        self,
        causality: str | None = None,
        variability: str | None = None,
    ) -> list[Fmi3ScalarVariable]:
        matches: list[Fmi3ScalarVariable] = []
        for variable in self.variables:
            if causality is not None and variable.causality != causality:
                continue
            if variability is not None and variable.variability != variability:
                continue
            matches.append(variable)
        return matches

    @property
    def inputs(self) -> list[Fmi3ScalarVariable]:
        return self.get(causality="input")

    @property
    def outputs(self) -> list[Fmi3ScalarVariable]:
        return self.get(causality="output")

    @property
    def parameters(self) -> list[Fmi3ScalarVariable]:
        return self.get(causality="parameter")

    def get_type_definitions(self, name: str | None = None, type_name: str | None = None) -> list[Fmi3TypeDefinition]:
        matches: list[Fmi3TypeDefinition] = []
        for definition in self.type_definitions:
            if name is not None and definition.name != name:
                continue
            if type_name is not None and definition.type_name != type_name:
                continue
            matches.append(definition)
        return matches

    def get_units(self, name: str | None = None) -> list[Fmi3Unit]:
        if name is None:
            return list(self.unit_definitions)
        return [unit for unit in self.unit_definitions if unit.name == name]