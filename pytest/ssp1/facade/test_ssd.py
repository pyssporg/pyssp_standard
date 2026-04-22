from __future__ import annotations

import shutil
from xml.etree import ElementTree as ET

from pyssp_standard.ssd import Component, Connection, Connector, DefaultExperiment, SSD, System
from pyssp_standard.standard.ssp1.model import Ssp1Annotation


def test_check_compliance_accepts_reference_fixture(embrace_ssd_fixture):
    with SSD(embrace_ssd_fixture) as ssd:
        assert ssd.check_compliance() is True


def test_create_round_trip(tmp_path):
    path = tmp_path / "test.ssd"

    with SSD(path, mode="w") as ssd:
        ssd.xml.name = "Test SSD"
        ssd.xml.version = "1.0"
        ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        component = Component()
        component.name = "component"
        component.component_type = "application/x-fmu-sharedlibrary"
        component.source = "resources/example.fmu"
        component.implementation = "CoSimulation"
        component.connectors.append(Connector(None, "x", "output", "Real"))

        ssd.xml.system = System(None, "system")
        ssd.xml.system.elements.append(component)
        ssd.xml.system.connectors.append(Connector(None, "x", "output", "Real"))
        ssd.xml.add_connection(Connection(start_element="component", start_connector="x", end_connector="x"))

    with SSD(path, mode="r") as ssd:
        assert ssd.xml.name == "Test SSD"
        assert ssd.xml.version == "1.0"
        assert ssd.xml.default_experiment is not None
        assert ssd.xml.default_experiment.start_time == 0.0
        assert ssd.xml.default_experiment.stop_time == 1.0
        assert ssd.xml.system is not None
        assert len(ssd.xml.system.elements) == 1
        assert len(ssd.xml.system.connectors) == 1
        assert len(ssd.xml.connections()) == 1
        assert ssd.xml.system.elements[0].component_type == "application/x-fmu-sharedlibrary"


def test_editing_connections_preserves_compliance(tmp_path, embrace_ssd_fixture):
    path = tmp_path / "fixture.ssd"
    shutil.copy(embrace_ssd_fixture, path)

    with SSD(path, "a") as ssd:
        ssd.xml.add_connection(
            Connection(start_element="house", start_connector="garage", end_element="work", end_connector="parking")
        )
        ssd.xml.remove_connection(
            Connection(
                start_element="Atmos",
                start_connector="Tamb",
                end_element="Consumer",
                end_connector="Tamb",
            )
        )
        assert ssd.check_compliance() is True

    with SSD(path) as ssd:
        assert len(ssd.xml.list_connectors(parent="Consumer")) == 76
        assert any(connection.start_element == "house" for connection in ssd.xml.connections())


def test_standalone_facade_preserves_external_binding_reference_without_resolution(mixed_ssd_fixture):
    with SSD(mixed_ssd_fixture) as ssd:
        assert len(ssd.xml.parameter_bindings) == 2
        external_binding = next(binding for binding in ssd.xml.parameter_bindings if binding.source is not None)
        assert external_binding.prefix == "Controller"
        assert external_binding.source == "external_values.ssv"
        assert external_binding.parameter_set is None
        assert external_binding.parameter_mapping is None


def test_list_connectors_returns_component_connectors(embrace_ssd_fixture):
    with SSD(embrace_ssd_fixture) as ssd:
        found = ssd.xml.list_connectors(parent="Consumer")

    assert len(found) == 76


def test_round_trip_preserves_metadata_and_connector_annotations(tmp_path):
    path = tmp_path / "annotations.ssd"

    with SSD(path, mode="w") as ssd:
        ssd.xml.name = "Annotated SSD"
        ssd.xml.version = "1.0"
        ssd.xml.metadata.annotations.append(
            Ssp1Annotation(
                type_name="com.example.doc",
                elements=[ET.fromstring('<doc xmlns="urn:test">ssd</doc>')],
            )
        )
        connector = Connector(None, "x", "output", "Real")
        connector.annotations.append(
            Ssp1Annotation(
                type_name="com.example.connector",
                elements=[ET.fromstring('<connectorNote xmlns="urn:test">signal</connectorNote>')],
            )
        )
        ssd.xml.system = System(None, "system")
        ssd.xml.system.connectors.append(connector)

    with SSD(path, mode="r") as ssd:
        assert ssd.xml.metadata.annotations[0].elements[0].text == "ssd"
        assert ssd.xml.system is not None
        assert ssd.xml.system.connectors[0].annotations[0].type_name == "com.example.connector"
        assert ssd.xml.system.connectors[0].annotations[0].elements[0].text == "signal"
