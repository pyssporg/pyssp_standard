from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from pyssp_standard.standard.ssp1.model.ssc_model import (
    Ssp1Annotation,
    Ssp1DocumentMetadata,
)
from pyssp_standard.standard.common.utils import ExternalReference
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet


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

    @staticmethod
    def connections_equal(left: Ssd1Connection, right: Ssd1Connection) -> bool:
        return (
            left.start_element == right.start_element
            and left.start_connector == right.start_connector
            and left.end_element == right.end_element
            and left.end_connector == right.end_connector
        )


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
        parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object]],
        *,
        binding_name: str | None = None,
        prefix: str | None = None,
        version: str = "1.0",
        metadata: Ssp1DocumentMetadata | None = None,
    ) -> "Ssd1ParameterBinding":
        from pyssp_standard.standard.ssp1.operations.ssd_parameter_bindings import (
            extend_inline_parameter_binding,
        )

        return extend_inline_parameter_binding(
            self.parameter_bindings,
            parameters,
            default_name=f"{self.name}_parameters",
            binding_name=binding_name,
            prefix=prefix,
            version=version,
            metadata=metadata,
        )


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
    elements: list[Ssd1Component | Ssd1System] = field(default_factory=list)
    connectors: list[Ssd1Connector] = field(default_factory=list)
    connections: list[Ssd1Connection] = field(default_factory=list)
    parameter_bindings: list[Ssd1ParameterBinding] = field(default_factory=list)

    def get_connections(self) -> list[Ssd1Connection]:
        return self.connections

    def get_components(self) -> list[Ssd1Component]:
        """Return only Ssd1Component children (not nested systems)."""
        return [e for e in self.elements if isinstance(e, Ssd1Component)]

    def get_subsystems(self) -> list[Ssd1System]:
        """Return only nested Ssd1System children."""
        return [e for e in self.elements if isinstance(e, Ssd1System)]

    def add_connection(self, connection: Ssd1Connection) -> Ssd1Connection:
        self.connections.append(connection)
        return connection

    def remove_connection(self, connection: Ssd1Connection) -> None:
        self.connections = [
            existing
            for existing in self.connections
            if not Ssd1Connection.connections_equal(existing, connection)
        ]

    def list_connectors(self, parent: str | None = None) -> list[Ssd1Connector]:
        if parent is None:
            return list(self.connectors)
        for element in self.elements:
            if element.name == parent:
                return list(element.connectors)
        return []

    def get_parameter_bindings(self) -> list[Ssd1ParameterBinding]:
        """Return system-level parameter bindings only."""
        return self.parameter_bindings

    def get_all_parameter_bindings(self) -> list[Ssd1ParameterBinding]:
        """Recursively collect parameter bindings from this system, all nested
        subsystems, and all direct component children.
        """
        result = list(self.parameter_bindings)
        for element in self.elements:
            if isinstance(element, Ssd1System):
                result.extend(element.get_all_parameter_bindings())
            elif isinstance(element, Ssd1Component):
                result.extend(element.parameter_bindings)
        return result

    def extend_inline_parameterset(
        self,
        parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object]],
        *,
        binding_name: str | None = None,
        prefix: str | None = None,
        version: str = "1.0",
        metadata: Ssp1DocumentMetadata | None = None,
    ) -> "Ssd1ParameterBinding":
        from pyssp_standard.standard.ssp1.operations.ssd_parameter_bindings import (
            extend_inline_parameter_binding,
        )

        return extend_inline_parameter_binding(
            self.parameter_bindings,
            parameters,
            default_name=f"{self.name}_parameters",
            binding_name=binding_name,
            prefix=prefix,
            version=version,
            metadata=metadata,
        )

    def add_external_parameterset(
        self,
        source: str,
        *,
        mapping_source: str | None = None,
        prefix: str | None = None,
    ) -> "Ssd1ParameterBinding":
        from pyssp_standard.standard.ssp1.operations.ssd_parameter_bindings import (
            add_external_parameterset,
        )

        return add_external_parameterset(
            self.parameter_bindings,
            source=source,
            mapping_source=mapping_source,
            prefix=prefix,
        )


@dataclass
class Ssd1SystemStructureDescription:
    name: str = "system"
    version: str = "1.0"
    metadata: Ssp1DocumentMetadata = field(default_factory=Ssp1DocumentMetadata)
    system: Ssd1System | None = None
    default_experiment: Ssd1DefaultExperiment | None = None
