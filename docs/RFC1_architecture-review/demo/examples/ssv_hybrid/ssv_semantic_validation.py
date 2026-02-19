from dataclasses import dataclass

from .ssv_model import ParameterSet


@dataclass
class Diagnostic:
    level: str
    message: str


class SemanticValidator:
    def validate_parameter_set(self, model: ParameterSet) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        seen = set()
        for p in model.parameters:
            if p.name in seen:
                diagnostics.append(Diagnostic("error", f"Duplicate parameter name: {p.name}"))
            seen.add(p.name)

            if p.type_name != "Real":
                diagnostics.append(Diagnostic("warning", f"Unsupported type in mockup: {p.type_name}"))

        if model.version != "2.0":
            diagnostics.append(Diagnostic("warning", f"Mockup expects SSP2 version 2.0, got {model.version}"))

        return diagnostics
