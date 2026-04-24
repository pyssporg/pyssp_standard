from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Iterable, Mapping, TypeVar

from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1Annotation, Ssp1DocumentMetadata
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet


ReferenceT = TypeVar("ReferenceT")


@dataclass
class Ssd1DefaultExperiment:
    start_time: float | None = None
    stop_time: float | None = None


@dataclass
class Ssd1Connector:
    element: str | None = None
    name: str = ""
    kind: str = ""
    type_name: str | None = None
    type_attributes: dict[str, str] = field(default_factory=dict)
    id: str | None = None
    description: str | None = None
    annotations: list[Ssp1Annotation] = field(default_factory=list)


@dataclass
class Ssd1Connection:
    start_element: str | None = None
    start_connector: str = ""
    end_element: str | None = None
    end_connector: str = ""


@dataclass
class Ssd1Component:
    name: str = ""
    source: str = ""
    component_type: str | None = None
    implementation: str | None = None
    connectors: list[Ssd1Connector] = field(default_factory=list)
    parameter_bindings: list["Ssd1ParameterBinding"] = field(default_factory=list)

    def extend_inline_parameterset(
        self,
        parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object] | Mapping[str, object]],
        *,
        binding_name: str | None = None,
        prefix: str | None = None,
        version: str = "1.0",
        metadata: Ssp1DocumentMetadata | None = None,
    ) -> "Ssd1ParameterBinding":
        binding = self._first_inline_parameter_binding()
        if binding is None:
            parameter_set = Ssp1ParameterSet(
                name=binding_name or f"{self.name}_parameters",
                version=version,
                metadata=metadata or Ssp1DocumentMetadata(),
            )
            binding = Ssd1ParameterBinding(prefix=prefix, parameter_set=parameter_set)
            self.parameter_bindings.append(binding)
        else:
            parameter_set = binding.parameter_set
            if parameter_set is None:
                raise RuntimeError(f"Inline parameter binding for component '{self.name}' has no parameter set")

            if binding_name is not None:
                parameter_set.name = binding_name
            if prefix is not None:
                binding.prefix = prefix
            if metadata is not None:
                parameter_set.metadata = metadata
            parameter_set.version = version

        parameter_set.extend_parameters(parameters)
        return binding

    def _first_inline_parameter_binding(self) -> "Ssd1ParameterBinding | None":
        for binding in self.parameter_bindings:
            if binding.parameter_set is not None and binding.source is None:
                return binding
        return None


@dataclass
class ExternalReference:
    source: str | None = None

    @property
    def is_external(self) -> bool:
        return self.source is not None

@dataclass
class Ssd1ParameterMappingReference(ExternalReference):
    mapping: Ssp1ParameterMapping | None = None

@dataclass
class Ssd1ParameterBinding(ExternalReference):
    prefix: str | None = None
    parameter_set: Ssp1ParameterSet | None = None
    parameter_mapping: Ssd1ParameterMappingReference | None = None


@dataclass
class Ssd1System:
    element: str | None = None
    name: str = ""
    elements: list[Ssd1Component] = field(default_factory=list)
    connectors: list[Ssd1Connector] = field(default_factory=list)
    connections: list[Ssd1Connection] = field(default_factory=list)
    parameter_bindings: list[Ssd1ParameterBinding] = field(default_factory=list)


@dataclass
class Ssd1SystemStructureDescription:
    name: str
    version: str
    metadata: Ssp1DocumentMetadata = field(default_factory=Ssp1DocumentMetadata)
    system: Ssd1System | None = None
    default_experiment: Ssd1DefaultExperiment | None = None

    def connections(self) -> list[Ssd1Connection]:
        if self.system is None:
            return []
        return self.system.connections

    def add_connection(self, connection: Ssd1Connection) -> Ssd1Connection:
        if self.system is None:
            self.system = Ssd1System(name="system")
        self.system.connections.append(connection)
        return connection

    def remove_connection(self, connection: Ssd1Connection) -> None:
        if self.system is None:
            return
        self.system.connections = [
            existing
            for existing in self.system.connections
            if not self._connections_equal(existing, connection)
        ]

    def list_connectors(self, parent: str | None = None) -> list[Ssd1Connector]:
        if self.system is None:
            return []
        if parent is None:
            return list(self.system.connectors)
        for element in self.system.elements:
            if element.name == parent:
                return list(element.connectors)
        return []

    @property
    def parameter_bindings(self) -> list[Ssd1ParameterBinding]:
        if self.system is None:
            return []
        return self.system.parameter_bindings

    @staticmethod
    def _connections_equal(left: Ssd1Connection, right: Ssd1Connection) -> bool:
        return (
            left.start_element == right.start_element
            and left.start_connector == right.start_connector
            and left.end_element == right.end_element
            and left.end_connector == right.end_connector
        )
