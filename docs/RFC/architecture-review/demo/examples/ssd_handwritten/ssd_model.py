from dataclasses import dataclass, field


@dataclass
class SsdComponent:
    name: str
    source: str


@dataclass
class SsdConnection:
    start_element: str
    start_connector: str
    end_element: str
    end_connector: str


@dataclass
class SsdDocument:
    name: str
    version: str
    components: list[SsdComponent] = field(default_factory=list)
    connections: list[SsdConnection] = field(default_factory=list)

    def add_component(self, name: str, source: str):
        self.components.append(SsdComponent(name=name, source=source))

    def add_connection(
        self,
        start_element: str,
        start_connector: str,
        end_element: str,
        end_connector: str,
    ):
        self.connections.append(
            SsdConnection(
                start_element=start_element,
                start_connector=start_connector,
                end_element=end_element,
                end_connector=end_connector,
            )
        )
