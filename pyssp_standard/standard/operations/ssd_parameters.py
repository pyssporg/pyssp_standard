from __future__ import annotations

from collections.abc import Iterable, Mapping

from pyssp_standard.standard.operations.ssd_parameter_bindings import extend_inline_parameter_binding
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1Component, Ssd1SystemStructureDescription
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter


def extend_component_parametersets(
    document: Ssd1SystemStructureDescription,
    parameters_by_component: Mapping[
        str,
        Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object] | Mapping[str, object]],
    ],
) -> None:
    system = document.system
    if system is None:
        raise RuntimeError("Cannot extend a parameter set without a system")

    components_by_name = {
        element.name: element
        for element in system.elements
        if isinstance(element, Ssd1Component)
    }

    for component_name, parameters in parameters_by_component.items():
        component = components_by_name.get(component_name)
        if component is None:
            raise KeyError(f"Component not found in system '{system.name}': {component_name}")

        extend_inline_parameter_binding(
            component.parameter_bindings,
            parameters,
            default_name=f"{component.name}_parameters",
            owner_name=f"component '{component.name}'",
        )
