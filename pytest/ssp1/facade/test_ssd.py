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


def test_component_can_extend_first_inline_parameterset_from_mapping(tmp_path):
    path = tmp_path / "inline_parameters.ssd"

    with SSD(path, mode="w") as ssd:
        component = Component(name="component", source="resources/example.fmu")
        component.extend_inline_parameterset(
            [
                ("gain", 2.5),
                {"name": "enabled", "value": True},
            ]
        )
        component.extend_inline_parameterset({"offset": -1})

        ssd.xml.name = "Inline Parameters"
        ssd.xml.version = "1.0"
        ssd.xml.system = System(None, "system")
        ssd.xml.system.elements.append(component)

    with SSD(path, mode="r") as ssd:
        component = ssd.xml.system.elements[0]
        binding = component.parameter_bindings[0]

        assert binding.parameter_set is not None
        assert binding.parameter_set.name == "component_parameters"
        assert len(component.parameter_bindings) == 1
        assert [(parameter.name, parameter.attributes["value"]) for parameter in binding.parameter_set.parameters] == [
            ("gain", "2.5"),
            ("enabled", "true"),
            ("offset", "-1"),
        ]


def test_ssd_can_extend_component_inline_parametersets_by_name(tmp_path):
    path = tmp_path / "facade_parameters.ssd"

    with SSD(path, mode="w") as ssd:
        component_a = Component(name="step", source="resources/step.fmu")
        component_b = Component(name="gain", source="resources/gain.fmu")

        ssd.xml.name = "Facade Parameters"
        ssd.xml.version = "1.0"
        ssd.xml.system = System(None, "system")
        ssd.xml.system.elements.extend([component_a, component_b])

        ssd.extend_parameterset(
            {
                "step": {"height": 2.0, "offset": 1.0},
                "gain": {"k": 3.0},
            }
        )

    with SSD(path, mode="r") as ssd:
        step = next(element for element in ssd.xml.system.elements if element.name == "step")
        gain = next(element for element in ssd.xml.system.elements if element.name == "gain")

        assert step.parameter_bindings[0].parameter_set is not None
        assert gain.parameter_bindings[0].parameter_set is not None
        assert [(parameter.name, parameter.attributes["value"]) for parameter in step.parameter_bindings[0].parameter_set.parameters] == [
            ("height", "2.0"),
            ("offset", "1.0"),
        ]
        assert [(parameter.name, parameter.attributes["value"]) for parameter in gain.parameter_bindings[0].parameter_set.parameters] == [
            ("k", "3.0"),
        ]


def test_round_trip_preserves_structural_order_in_serialized_xml(tmp_path):
    path = tmp_path / "ordered.ssd"
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ssd:SystemStructureDescription xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon" xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructureDescription" version="1.0" name="Ordered SSD">
  <ssd:System name="system">
    <ssd:Connectors>
      <ssd:Connector kind="output" name="beta_bus"><ssc:Real /></ssd:Connector>
      <ssd:Connector kind="output" name="alpha_bus"><ssc:Real /></ssd:Connector>
    </ssd:Connectors>
    <ssd:Elements>
      <ssd:Component source="resources/beta.fmu" name="beta_component" type="application/x-fmu-sharedlibrary"><ssd:Connectors><ssd:Connector kind="output" name="beta_out"><ssc:Real /></ssd:Connector></ssd:Connectors></ssd:Component>
      <ssd:Component name="alpha_component" source="resources/alpha.fmu" type="application/x-fmu-sharedlibrary"><ssd:Connectors><ssd:Connector name="alpha_out" kind="output"><ssc:Real /></ssd:Connector></ssd:Connectors></ssd:Component>
    </ssd:Elements>
    <ssd:Connections>
      <ssd:Connection endConnector="beta_bus" startConnector="beta_out" startElement="beta_component" />
      <ssd:Connection startElement="alpha_component" startConnector="alpha_out" endConnector="alpha_bus" />
    </ssd:Connections>
  </ssd:System>
</ssd:SystemStructureDescription>
""",
        encoding="utf-8",
    )

    with SSD(path, mode="a"):
        pass

    with SSD(path, mode="r") as ssd:
        assert [element.name for element in ssd.xml.system.elements] == ["beta_component", "alpha_component"]
        assert [connector.name for connector in ssd.xml.system.connectors] == ["beta_bus", "alpha_bus"]
        assert [connection.start_element for connection in ssd.xml.connections()] == ["beta_component", "alpha_component"]

    xml_text = path.read_text(encoding="utf-8")
    assert xml_text.index('name="beta_component"') < xml_text.index('name="alpha_component"')
    assert xml_text.index('name="beta_bus"') < xml_text.index('name="alpha_bus"')
    assert xml_text.index('startElement="beta_component"') < xml_text.index('startElement="alpha_component"')
