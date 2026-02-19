from dataclasses import dataclass, field

from .parameter_model import ParameterSet


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


@dataclass
class SsdDocument:
    name: str
    version: str
    components: list[SsdComponent] = field(default_factory=list)
    parameter_bindings: list[SsdParameterBinding] = field(default_factory=list)

    def add_component(self, name: str, source: str):
        self.components.append(SsdComponent(name=name, source=source))
