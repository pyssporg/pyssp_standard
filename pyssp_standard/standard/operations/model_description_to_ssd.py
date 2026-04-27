from __future__ import annotations

from pyssp_standard.standard.fmi2.model.model_description import Fmi2ModelDescriptionDocument
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1System,
    Ssd1SystemStructureDescription,
)


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


def add_component_to_system_structure(
    document: Ssd1SystemStructureDescription,
    component: Ssd1Component,
    *,
    expose_system_connectors: bool = False,
    connector_prefix: str | None = None,
    default_system_name: str = "system",
) -> None:
    if document.system is None:
        document.system = Ssd1System(name=document.name or default_system_name)

    document.system.elements.append(component)

    if not expose_system_connectors:
        return

    for component_connector in component.connectors:
        connector_name = (
            f"{connector_prefix}{component_connector.name}"
            if connector_prefix
            else component_connector.name
        )
        system_connector = Ssd1Connector(
            name=connector_name,
            kind=component_connector.kind,
            type_name=component_connector.type_name,
            type_attributes=dict(component_connector.type_attributes),
        )
        document.system.connectors.append(system_connector)

        if component_connector.kind == "output":
            document.system.connections.append(
                Ssd1Connection(
                    start_element=component.name,
                    start_connector=component_connector.name,
                    end_connector=connector_name,
                )
            )
        else:
            document.system.connections.append(
                Ssd1Connection(
                    start_connector=connector_name,
                    end_element=component.name,
                    end_connector=component_connector.name,
                )
            )
