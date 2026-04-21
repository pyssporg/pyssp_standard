from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SsdDefaultExperiment:
    start_time: float | None = None
    stop_time: float | None = None


@dataclass
class SsdConnector:
    element: str | None = None
    name: str = ""
    kind: str = ""
    type_name: str | None = None
    type_attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class SsdConnection:
    start_element: str | None = None
    start_connector: str = ""
    end_element: str | None = None
    end_connector: str = ""


@dataclass
class SsdComponent:
    name: str = ""
    source: str = ""
    component_type: str | None = None
    implementation: str | None = None
    connectors: list[SsdConnector] = field(default_factory=list)


@dataclass
class SsdSystem:
    element: str | None = None
    name: str = ""
    elements: list[SsdComponent] = field(default_factory=list)
    connectors: list[SsdConnector] = field(default_factory=list)
    connections: list[SsdConnection] = field(default_factory=list)


@dataclass
class SsdSystemStructureDescription:
    name: str
    version: str
    system: SsdSystem | None = None
    default_experiment: SsdDefaultExperiment | None = None

    def connections(self) -> list[SsdConnection]:
        if self.system is None:
            return []
        return self.system.connections

    def add_connection(self, connection: SsdConnection) -> SsdConnection:
        if self.system is None:
            self.system = SsdSystem(name="system")
        self.system.connections.append(connection)
        return connection

    def remove_connection(self, connection: SsdConnection) -> None:
        if self.system is None:
            return
        self.system.connections = [
            existing
            for existing in self.system.connections
            if not self._connections_equal(existing, connection)
        ]

    def list_connectors(self, parent: str | None = None) -> list[SsdConnector]:
        if self.system is None:
            return []
        if parent is None:
            return list(self.system.connectors)
        for element in self.system.elements:
            if element.name == parent:
                return list(element.connectors)
        return []

    @staticmethod
    def _connections_equal(left: SsdConnection, right: SsdConnection) -> bool:
        return (
            left.start_element == right.start_element
            and left.start_connector == right.start_connector
            and left.end_element == right.end_element
            and left.end_connector == right.end_connector
        )
