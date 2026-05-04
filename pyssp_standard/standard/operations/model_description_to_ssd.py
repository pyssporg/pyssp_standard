from __future__ import annotations

from pyssp_standard.standard.fmi2.model.model_description import Fmi2ModelDescriptionDocument
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1Component, Ssd1Connector


def ssp_connector_type_attributes(variable) -> dict[str, str]:
    if variable.type_name == "Real":
        return {
            key: value
            for key, value in variable.type_attributes.items()
            if key == "unit"
        }
    if variable.type_name == "Binary":
        return {
            key: value
            for key, value in variable.type_attributes.items()
            if key == "mime-type"
        }
    if variable.type_name == "Enumeration" and variable.declared_type is not None:
        return {"name": variable.declared_type}
    return {}


def create_component_from_model_description(
    model_description: Fmi2ModelDescriptionDocument,
    *,
    component_name: str,
    source: str,
    implementation: str | None = "ModelExchange",
    component_type: str | None = "application/x-fmu-sharedlibrary",
) -> Ssd1Component:
    component = Ssd1Component(
        name=component_name,
        source=source,
        component_type=component_type,
        implementation=implementation,
    )

    for variable in list(model_description.parameters) + list(model_description.inputs) + list(model_description.outputs):
        connector = Ssd1Connector(
            name=variable.name,
            kind=variable.causality or "",
            type_name=variable.type_name,
            type_attributes=ssp_connector_type_attributes(variable),
        )
        component.connectors.append(connector)

    return component
