from __future__ import annotations

import pytest

from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1ParameterBinding,
    Ssd1System,
    Ssd1SystemStructureDescription,
)
from pyssp_standard.standard.ssp1.operations.ssd_flatten import flatten_ssd


class TestFlattenSsd:
    """Test suite for the SSD flatten operation."""

    def test_flatten_simple_subsystem(self):
        """Components inside a subsystem receive an underscore-prefixed name."""
        inner = Ssd1Component(name="comp", source="test.fmu")
        subsystem = Ssd1System(name="sub", elements=[inner])
        root = Ssd1System(name="root", elements=[subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        assert len(result.system.elements) == 1
        promoted = result.system.elements[0]
        assert promoted.name == "sub_comp"
        assert isinstance(promoted, Ssd1Component)

    def test_preserves_root_components(self):
        """Root-level components are kept unchanged alongside promoted ones."""
        root_comp = Ssd1Component(name="root_comp", source="test.fmu")
        inner = Ssd1Component(name="inner", source="test.fmu")
        subsystem = Ssd1System(name="sub", elements=[inner])
        root = Ssd1System(name="root", elements=[root_comp, subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        names = {e.name for e in result.system.elements}
        assert "root_comp" in names
        assert "sub_inner" in names
        assert len(result.system.elements) == 2

    def test_remaps_internal_connections(self):
        """Component-to-component connections within a subsystem are
        rewritten with the new prefixed names."""
        comp_a = Ssd1Component(name="A", source="a.fmu")
        comp_b = Ssd1Component(name="B", source="b.fmu")
        conn = Ssd1Connection(
            start_element="A", start_connector="out",
            end_element="B", end_connector="in",
        )
        subsystem = Ssd1System(
            name="sub", elements=[comp_a, comp_b], connections=[conn],
        )
        root = Ssd1System(name="root", elements=[subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        assert len(result.system.connections) == 1
        c = result.system.connections[0]
        assert c.start_element == "sub_A"
        assert c.end_element == "sub_B"
        assert c.start_connector == "out"
        assert c.end_connector == "in"

    def test_traces_cross_level_connections(self):
        """Connections that reference a subsystem connector are traced
        through to the actual internal component."""
        inner = Ssd1Component(name="inner", source="test.fmu")
        sub_conn_in = Ssd1Connection(
            start_element=None, start_connector="input",
            end_element="inner", end_connector="in",
        )
        sub_conn_out = Ssd1Connection(
            start_element="inner", start_connector="out",
            end_element=None, end_connector="output",
        )
        sub_connectors = [
            Ssd1Connector(name="input", kind="input"),
            Ssd1Connector(name="output", kind="output"),
        ]
        subsystem = Ssd1System(
            name="sub",
            elements=[inner],
            connectors=sub_connectors,
            connections=[sub_conn_in, sub_conn_out],
        )

        src = Ssd1Component(name="source", source="src.fmu")
        root_conn1 = Ssd1Connection(
            start_element="source", start_connector="out",
            end_element="sub", end_connector="input",
        )
        root_conn2 = Ssd1Connection(
            start_element="sub", start_connector="output",
            end_element="source", end_connector="in",
        )
        root = Ssd1System(
            name="root",
            elements=[src, subsystem],
            connections=[root_conn1, root_conn2],
        )
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        conn_set = {
            (c.start_element, c.start_connector, c.end_element, c.end_connector)
            for c in result.system.connections
        }
        assert ("source", "out", "sub_inner", "in") in conn_set
        assert ("sub_inner", "out", "source", "in") in conn_set

    def test_recursive_subsystem_tracing(self):
        """Multi-level subsystem connector tunnelling resolves correctly."""
        core = Ssd1Component(name="core", source="core.fmu")
        sub_a_conn_in = Ssd1Connection(
            start_element=None, start_connector="in",
            end_element="core", end_connector="in",
        )
        sub_a_conn_out = Ssd1Connection(
            start_element="core", start_connector="out",
            end_element=None, end_connector="out",
        )
        sub_a = Ssd1System(
            name="a",
            elements=[core],
            connectors=[
                Ssd1Connector(name="in"),
                Ssd1Connector(name="out"),
            ],
            connections=[sub_a_conn_in, sub_a_conn_out],
        )

        sub_b_conn_in = Ssd1Connection(
            start_element=None, start_connector="in",
            end_element="a", end_connector="in",
        )
        sub_b_conn_out = Ssd1Connection(
            start_element="a", start_connector="out",
            end_element=None, end_connector="out",
        )
        sub_b = Ssd1System(
            name="b",
            elements=[sub_a],
            connectors=[
                Ssd1Connector(name="in"),
                Ssd1Connector(name="out"),
            ],
            connections=[sub_b_conn_in, sub_b_conn_out],
        )

        src = Ssd1Component(name="src", source="src.fmu")
        dst = Ssd1Component(name="dst", source="dst.fmu")
        root_conn1 = Ssd1Connection(
            start_element="src", start_connector="out",
            end_element="b", end_connector="in",
        )
        root_conn2 = Ssd1Connection(
            start_element="b", start_connector="out",
            end_element="dst", end_connector="in",
        )
        root = Ssd1System(
            name="root",
            elements=[src, dst, sub_b],
            connections=[root_conn1, root_conn2],
        )
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        promoted_names = {e.name for e in result.system.elements}
        assert "b_a_core" in promoted_names
        assert len(result.system.elements) == 3

        conn_set = {
            (c.start_element, c.start_connector, c.end_element, c.end_connector)
            for c in result.system.connections
        }
        assert ("src", "out", "b_a_core", "in") in conn_set
        assert ("b_a_core", "out", "dst", "in") in conn_set

    def test_merges_parameter_bindings(self):
        """Parameter bindings from nested subsystems are merged into the
        root system.  Component-level bindings remain on the component,
        NOT duplicated at the system level."""
        comp = Ssd1Component(
            name="comp", source="test.fmu",
            parameter_bindings=[Ssd1ParameterBinding(prefix="p")],
        )
        subsystem = Ssd1System(
            name="sub", elements=[comp],
            parameter_bindings=[Ssd1ParameterBinding(prefix="s")],
        )
        root = Ssd1System(name="root", elements=[subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        # System-level: only subsystem's bindings (not component's)
        assert len(result.system.parameter_bindings) == 1
        assert result.system.parameter_bindings[0].prefix == "s"

        # Component-level: promoted component keeps its own binding
        promoted = result.system.elements[0]
        assert promoted.name == "sub_comp"
        assert len(promoted.parameter_bindings) == 1
        assert promoted.parameter_bindings[0].prefix == "p"

    def test_cross_file_reference_raises_value_error(self):
        """A subsystem with a non-None ``element`` (cross-file pointer)
        causes a ValueError."""
        subsystem = Ssd1System(name="sub", element="other.ssd")
        root = Ssd1System(name="root", elements=[subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        with pytest.raises(ValueError, match="cross-file reference"):
            flatten_ssd(doc)

    def test_empty_system_raises_value_error(self):
        """An SSD with no system raises ValueError."""
        doc = Ssd1SystemStructureDescription(name="test", system=None)

        with pytest.raises(ValueError, match="no system"):
            flatten_ssd(doc)

    def test_idempotent_on_already_flat(self):
        """Flattening an already-flat system returns an equivalent
        structure (same names, connections preserved)."""
        comp_a = Ssd1Component(name="A", source="a.fmu")
        comp_b = Ssd1Component(name="B", source="b.fmu")
        conn = Ssd1Connection(
            start_element="A", start_connector="out",
            end_element="B", end_connector="in",
        )
        root = Ssd1System(
            name="root", elements=[comp_a, comp_b], connections=[conn],
        )
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        assert result.system.elements[0].name == "A"
        assert result.system.elements[1].name == "B"
        assert result.system.connections[0].start_element == "A"

    def test_no_subsystems_remain(self):
        """After flattening, no Ssd1System instances exist in the
        root system's elements list."""
        inner = Ssd1Component(name="inner", source="test.fmu")
        subsystem = Ssd1System(name="sub", elements=[inner])
        root = Ssd1System(name="root", elements=[subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        assert not any(
            isinstance(e, Ssd1System) for e in result.system.elements
        )

    def test_name_collision_raises_value_error(self):
        """A promoted name that collides with an existing root component
        raises ValueError."""
        inner = Ssd1Component(name="existing", source="test.fmu")
        subsystem = Ssd1System(name="sub", elements=[inner])
        root_comp = Ssd1Component(name="sub_existing", source="test.fmu")
        root = Ssd1System(name="root", elements=[root_comp, subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        with pytest.raises(ValueError, match="collision"):
            flatten_ssd(doc)

    def test_degenerate_empty_subsystem(self):
        """A subsystem with no elements is handled gracefully (contributes
        nothing to the output)."""
        subsystem = Ssd1System(name="empty", elements=[])
        root = Ssd1System(name="root", elements=[subsystem])
        doc = Ssd1SystemStructureDescription(name="test", system=root)

        result = flatten_ssd(doc)

        assert len(result.system.elements) == 0
        assert not any(
            isinstance(e, Ssd1System) for e in result.system.elements
        )
