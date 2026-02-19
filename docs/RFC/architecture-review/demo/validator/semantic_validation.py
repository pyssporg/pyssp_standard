from dataclasses import dataclass

from ..model.ssd_model import SsdDocument


@dataclass
class Diagnostic:
    level: str
    message: str


class SsdBindingValidator:
    def validate(self, doc: SsdDocument) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        component_names = {c.name for c in doc.components}
        for binding in doc.parameter_bindings:
            if binding.target not in component_names:
                diagnostics.append(Diagnostic("error", f"Unknown binding target: {binding.target}"))
            if binding.parameter_set is None:
                diagnostics.append(Diagnostic("error", f"Missing ParameterSet for target: {binding.target}"))

        return diagnostics
