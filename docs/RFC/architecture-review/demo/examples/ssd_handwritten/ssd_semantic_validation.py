from dataclasses import dataclass

from .ssd_model import SsdDocument


@dataclass
class SsdDiagnostic:
    level: str
    message: str


class SsdSemanticValidator:
    def validate(self, doc: SsdDocument) -> list[SsdDiagnostic]:
        diagnostics: list[SsdDiagnostic] = []

        names = [c.name for c in doc.components]
        duplicates = {name for name in names if names.count(name) > 1}
        for name in sorted(duplicates):
            diagnostics.append(SsdDiagnostic("error", f"Duplicate component name: {name}"))

        component_names = {c.name for c in doc.components}
        for con in doc.connections:
            if con.start_element and con.start_element not in component_names:
                diagnostics.append(
                    SsdDiagnostic("error", f"Unknown start component: {con.start_element}")
                )
            if con.end_element and con.end_element not in component_names:
                diagnostics.append(SsdDiagnostic("error", f"Unknown end component: {con.end_element}"))

        return diagnostics
