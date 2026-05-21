"""SSD flatten operation: promote all nested components to root with underscore-prefixed names.

This is a pure function that returns a new Ssd1SystemStructureDescription. The
input document is never mutated.
"""

from __future__ import annotations

from dataclasses import replace

from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1ParameterBinding,
    Ssd1System,
    Ssd1SystemStructureDescription,
)


def flatten_ssd(doc: Ssd1SystemStructureDescription) -> Ssd1SystemStructureDescription:
    """Flatten all nested subsystems, promoting components to root.

    Each promoted component receives an underscore-prefixed name built from the
    names of its ancestor subsystems.  All connections are remapped,
    cross-subsystem connectors are traced to their actual targets, and
    parameter bindings from every level are merged into the root.

    Args:
        doc: The SSD document to flatten.

    Returns:
        A new SSD document whose root system contains only Ssd1Component
        instances (no Ssd1System children).

    Raises:
        ValueError: If the document has no system, if any nested system
            has a cross-file reference (``element`` is not None), or if
            component name collisions occur after prefixing.
    """
    if doc.system is None:
        raise ValueError("Cannot flatten an SSD with no system")

    _reject_cross_file_refs(doc.system)

    components, name_map, root_names = _collect_and_prefix(doc.system)
    _check_collisions(name_map, root_names)

    connections = _flatten_root_connections(doc.system, name_map)
    connections.extend(_collect_internal_connections(doc.system, name_map))

    param_bindings = _collect_system_bindings(doc.system)

    new_system = Ssd1System(
        element=None,
        name=doc.system.name,
        elements=components,
        connectors=list(doc.system.connectors),
        connections=connections,
        parameter_bindings=param_bindings,
    )

    return Ssd1SystemStructureDescription(
        name=doc.name,
        version=doc.version,
        metadata=doc.metadata,
        system=new_system,
        default_experiment=doc.default_experiment,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _reject_cross_file_refs(system: Ssd1System) -> None:
    """Walk the system tree and raise ValueError if any system has an
    external ``element`` reference (cross-file pointer)."""
    if system.element is not None:
        raise ValueError(
            f"Cannot flatten system '{system.name}': "
            f"cross-file reference 'element={system.element}'"
        )
    for element in system.elements:
        if isinstance(element, Ssd1System):
            _reject_cross_file_refs(element)


def _collect_and_prefix(
    system: Ssd1System,
    prefix: str = "",
) -> tuple[list[Ssd1Component], dict[str, str], set[str]]:
    """Recursively collect components and build the old-name -> new-name map.

    Returns a 3-tuple:
        * flat list of promoted / root-kept Ssd1Component instances
        * mapping ``{old_name: new_name}`` for every renamed component
        * set of root-level component names (used for collision detection)
    """
    components: list[Ssd1Component] = []
    name_map: dict[str, str] = {}
    root_names: set[str] = set()

    for element in system.elements:
        if isinstance(element, Ssd1System):
            sub_prefix = f"{prefix}{element.name}_"
            sub_comps, sub_map, _ = _collect_and_prefix(element, sub_prefix)
            components.extend(sub_comps)
            name_map.update(sub_map)
        elif isinstance(element, Ssd1Component):
            if prefix:
                new_name = f"{prefix}{element.name}"
                name_map[element.name] = new_name
                promoted = Ssd1Component(
                    name=new_name,
                    source=element.source,
                    component_type=element.component_type,
                    implementation=element.implementation,
                    connectors=list(element.connectors),
                    parameter_bindings=list(element.parameter_bindings),
                )
                components.append(promoted)
            else:
                root_names.add(element.name)
                components.append(element)

    return components, name_map, root_names


def _collect_system_bindings(system: Ssd1System) -> list[Ssd1ParameterBinding]:
    """Collect parameter bindings from this system and all nested subsystems,
    NOT from components (which keep their own bindings)."""
    result = [replace(b) for b in system.parameter_bindings]
    for element in system.elements:
        if isinstance(element, Ssd1System):
            result.extend(_collect_system_bindings(element))
    return result


def _check_collisions(name_map: dict[str, str], root_names: set[str]) -> None:
    """Raise ValueError if any promoted component name collides with an
    existing root name or with another promoted name."""
    seen = set(root_names)
    for new_name in name_map.values():
        if new_name in seen:
            raise ValueError(
                f"Name collision after flattening: "
                f"component '{new_name}' already exists"
            )
        seen.add(new_name)


def _trace_subsystem_ref(
    context: Ssd1System,
    element_name: str | None,
    connector_name: str,
    name_map: dict[str, str],
) -> tuple[str | None, str]:
    """Resolve an endpoint that *may* point to a subsystem connector.

    * ``None`` connector stub               -> ``(None, connector_name)``
    * Renamed component                      -> ``(name_map[name], connector_name)``
    * Subsystem connector (within *context*) -> trace through recursively
    * Everything else                        -> ``(element_name, connector_name)``
    """
    if element_name is None:
        return None, connector_name

    if element_name in name_map:
        return name_map[element_name], connector_name

    for elem in context.elements:
        if isinstance(elem, Ssd1System) and elem.name == element_name:
            for conn in elem.connections:
                if conn.start_element is None and conn.start_connector == connector_name:
                    return _trace_subsystem_ref(
                        elem, conn.end_element, conn.end_connector, name_map,
                    )
                if conn.end_element is None and conn.end_connector == connector_name:
                    return _trace_subsystem_ref(
                        elem, conn.start_element, conn.start_connector, name_map,
                    )
            break

    return element_name, connector_name


def _flatten_root_connections(
    system: Ssd1System,
    name_map: dict[str, str],
) -> list[Ssd1Connection]:
    """Process the root system's own connections.

    Each endpoint is resolved via ``_trace_subsystem_ref`` so that
    references to subsystem connectors are followed to their actual
    target component.
    """
    result: list[Ssd1Connection] = []
    for conn in system.connections:
        start_elem, start_conn = _trace_subsystem_ref(
            system, conn.start_element, conn.start_connector, name_map,
        )
        end_elem, end_conn = _trace_subsystem_ref(
            system, conn.end_element, conn.end_connector, name_map,
        )
        if start_elem is not None or end_elem is not None:
            result.append(
                Ssd1Connection(
                    start_element=start_elem,
                    start_connector=start_conn,
                    end_element=end_elem,
                    end_connector=end_conn,
                )
            )
    return result


def _collect_internal_connections(
    system: Ssd1System,
    name_map: dict[str, str],
) -> list[Ssd1Connection]:
    """Recursively collect component-to-component connections from every
    subsystem.  Connections that reference a subsystem connector (either
    endpoint is ``None``) are *skipped* -- they are used only for tracing
    and have already been resolved at the parent level.
    """
    result: list[Ssd1Connection] = []
    for element in system.elements:
        if isinstance(element, Ssd1System):
            for conn in element.connections:
                if conn.start_element is not None and conn.end_element is not None:
                    result.append(
                        Ssd1Connection(
                            start_element=name_map.get(
                                conn.start_element, conn.start_element,
                            ),
                            start_connector=conn.start_connector,
                            end_element=name_map.get(
                                conn.end_element, conn.end_element,
                            ),
                            end_connector=conn.end_connector,
                        )
                    )
            result.extend(_collect_internal_connections(element, name_map))
    return result
