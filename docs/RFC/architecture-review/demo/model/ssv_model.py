from dataclasses import dataclass, field


@dataclass
class Parameter:
    name: str
    type_name: str
    value: str


@dataclass
class ParameterSet:
    name: str
    version: str
    parameters: list[Parameter] = field(default_factory=list)

    def add_real_parameter(self, name: str, value: float):
        self.parameters.append(Parameter(name=name, type_name="Real", value=str(value)))
