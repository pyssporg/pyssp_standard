from __future__ import annotations

import shutil

from pyssp_standard.ssd import Component, Connection, Connector, DefaultExperiment, SSD, System


def test_check_compliance_accepts_reference_fixture(embrace_ssd_fixture):
    with SSD(embrace_ssd_fixture) as ssd:
        assert ssd.check_compliance() is True


def test_create_round_trip(tmp_path):
    path = tmp_path / "test.ssd"

    with SSD(path, mode="w") as ssd:
        ssd.name = "Test SSD"
        ssd.version = "1.0"
        ssd.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        component = Component()
        component.name = "component"
        component.component_type = "application/x-fmu-sharedlibrary"
        component.source = "resources/example.fmu"
        component.implementation = "CoSimulation"
        component.connectors.append(Connector(None, "x", "output", "Real"))

        ssd.system = System(None, "system")
        ssd.system.elements.append(component)
        ssd.system.connectors.append(Connector(None, "x", "output", "Real"))
        ssd.add_connection(Connection(start_element="component", start_connector="x", end_connector="x"))

    with SSD(path, mode="r") as ssd:
        assert ssd.name == "Test SSD"
        assert ssd.version == "1.0"
        assert ssd.default_experiment is not None
        assert ssd.default_experiment.start_time == 0.0
        assert ssd.default_experiment.stop_time == 1.0
        assert ssd.system is not None
        assert len(ssd.system.elements) == 1
        assert len(ssd.system.connectors) == 1
        assert len(ssd.connections()) == 1
        assert ssd.system.elements[0].component_type == "application/x-fmu-sharedlibrary"


def test_editing_connections_preserves_compliance(tmp_path, embrace_ssd_fixture):
    path = tmp_path / "fixture.ssd"
    shutil.copy(embrace_ssd_fixture, path)

    with SSD(path, "a") as ssd:
        ssd.add_connection(
            Connection(start_element="house", start_connector="garage", end_element="work", end_connector="parking")
        )
        ssd.remove_connection(
            Connection(
                start_element="Atmos",
                start_connector="Tamb",
                end_element="Consumer",
                end_connector="Tamb",
            )
        )
        assert ssd.check_compliance() is True

    with SSD(path) as ssd:
        assert len(ssd.list_connectors(parent="Consumer")) == 76
        assert any(connection.start_element == "house" for connection in ssd.connections())


def test_standalone_facade_preserves_external_binding_reference_without_resolution(mixed_ssd_fixture):
    with SSD(mixed_ssd_fixture) as ssd:
        assert len(ssd.parameter_bindings) == 2
        external_binding = next(binding for binding in ssd.parameter_bindings if not binding.is_inlined)
        assert external_binding.prefix == "Controller"
        assert external_binding.external_path == "external_values.ssv"
        assert external_binding.parameter_set is None
        assert external_binding.parameter_mapping is None


def test_list_connectors_returns_component_connectors(embrace_ssd_fixture):
    with SSD(embrace_ssd_fixture) as ssd:
        found = ssd.list_connectors(parent="Consumer")

    assert len(found) == 76
