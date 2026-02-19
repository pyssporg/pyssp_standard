from dataclasses import dataclass, field

from .ssv_model import ParameterSet


@dataclass
class SsdComponent:
    name: str
    source: str


@dataclass
class SsdParameterBinding:
    target: str
    mode: str  # inline | external
    parameter_set: ParameterSet | None = None
    external_path: str | None = None
    is_internal: bool = False
    is_external: bool = False
    is_resolved: bool = False


@dataclass
class SsdDocument:
    name: str
    version: str
    components: list[SsdComponent] = field(default_factory=list)
    parameter_bindings: list[SsdParameterBinding] = field(default_factory=list)

    def add_component(self, name: str, source: str):
        self.components.append(SsdComponent(name=name, source=source))
