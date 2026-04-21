from __future__ import annotations

from pathlib import Path

from pyssp_standard.ssd import Component, Connection, Connector, DefaultExperiment, SSD, System
from pyssp_standard.ssm import SSM, Ssp1Transformation
from pyssp_standard.standard.ssp1.codec import Ssp1SsdXmlCodec, Ssp1SsmXmlCodec
from pyssp_standard.ssv import SSV


SSD_FIXTURE = Path("pytest/doc/embrace/SystemStructure.ssd")
SSM_FIXTURE = Path("pytest/doc/embrace/resources/ECS_HW.ssm")
MIXED_SSD_FIXTURE = Path("pytest/doc/mixed_example.ssd")
EXTERNAL_SSV_FIXTURE = Path("pytest/doc/external_values.ssv")


def test_ssp1_ssd_codec_parses_typed_fixture():
    document = Ssp1SsdXmlCodec().parse(SSD_FIXTURE.read_text(encoding="utf-8"))

    assert document.name == "embrace"
    assert document.version == "1.0"
    assert document.system is not None
    assert document.system.name == "root"
    assert len(document.system.elements) == 5
    assert len(document.system.connections) > 10
    assert len(document.parameter_bindings) == 1
    binding = document.parameter_bindings[0]
    assert binding.external_path == "resources/RAPID_Systems_2021-03-29_Test_1.ssv"
    assert binding.parameter_mapping_path == "resources/ECS_HW.ssm"
    assert binding.parameter_mapping is None
    assert binding.is_mapping_resolved is False


def test_ssp1_ssd_codec_parses_inline_and_external_parameter_bindings():
    codec = Ssp1SsdXmlCodec()
    document = codec.parse(MIXED_SSD_FIXTURE.read_text(encoding="utf-8"))

    assert document.system is not None
    assert len(document.parameter_bindings) == 2

    inline_binding = document.parameter_bindings[0]
    assert inline_binding.target == "Plant"
    assert inline_binding.is_inlined is True
    assert inline_binding.parameter_set is not None
    assert inline_binding.parameter_set.name == "PlantInline"
    assert inline_binding.parameter_set.parameters[0].name == "gain"
    assert inline_binding.parameter_set.parameters[0].attributes["value"] == "1.5"

    external_binding = document.parameter_bindings[1]
    assert external_binding.target == "Controller"
    assert external_binding.is_inlined is False
    assert external_binding.external_path == "external_values.ssv"
    assert external_binding.parameter_set is None

    reparsed = codec.parse(codec.serialize(document))
    assert len(reparsed.parameter_bindings) == 2
    assert reparsed.parameter_bindings[0].parameter_set is not None
    assert reparsed.parameter_bindings[0].parameter_set.parameters[0].attributes["value"] == "1.5"
    assert reparsed.parameter_bindings[1].external_path == "external_values.ssv"


def test_ssp1_ssm_codec_parses_typed_fixture():
    document = Ssp1SsmXmlCodec().parse(SSM_FIXTURE.read_text(encoding="utf-8"))

    assert document.version == "1.0"
    assert len(document.mappings) > 10
    assert document.mappings[0].target == "ECS_HW.reqCoolingTemperature"


def test_ssd_facade_create_round_trip(tmp_path):
    path = tmp_path / "test.ssd"

    with SSD(path, mode="w") as ssd:
        ssd.name = "Test SSD"
        ssd.version = "1.0"
        ssd.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        component = Component()
        component.name = "component"
        component.component_type = "application/x-fmu-sharedlibrary"
        component.source = "resources/example.fmu"
        component.connectors.append(Connector(None, "x", "output", "Real"))

        ssd.system = System(None, "system")
        ssd.system.elements.append(component)
        ssd.system.connectors.append(Connector(None, "x", "output", "Real"))
        ssd.add_connection(Connection(start_element="component", start_connector="x", end_connector="x"))
        ssd.check_compliance()

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


def test_ssd_facade_modifies_fixture(tmp_path):
    path = tmp_path / "fixture.ssd"
    path.write_text(SSD_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

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
        ssd.check_compliance()

    with SSD(path) as ssd:
        assert len(ssd.list_connectors(parent="Consumer")) == 76
        assert any(connection.start_element == "house" for connection in ssd.connections())


def test_ssm_facade_create_and_edit(tmp_path):
    path = tmp_path / "test.ssm"

    with SSM(path, "w") as ssm:
        ssm.add_mapping("dog", "shepard")
        ssm.add_mapping(
            "cat",
            "odd",
            transformation=Ssp1Transformation("LinearTransformation", {"factor": 2, "offset": 0}),
        )
        ssm.check_compliance()

    with SSM(path, "a") as ssm:
        ssm.edit_mapping(target="shepard", source="tax", suppress_unit_conversion=True)
        ssm.check_compliance()

    with SSM(path) as ssm:
        assert len(ssm.mappings) == 2
        assert ssm.mappings[0].source == "tax"
        assert ssm.mappings[0].suppress_unit_conversion is True
        assert ssm.mappings[1].transformation is not None
        assert ssm.mappings[1].transformation.type_name == "LinearTransformation"


def test_ssm_fixture_compliance():
    with SSM(SSM_FIXTURE) as ssm:
        ssm.check_compliance()
        assert len(ssm.mappings) == 203


def test_ssd_facade_preserves_external_binding_reference_and_ssv_loads_separately():
    with SSD(MIXED_SSD_FIXTURE) as ssd:
        assert len(ssd.parameter_bindings) == 2
        external_binding = next(binding for binding in ssd.parameter_bindings if not binding.is_inlined)
        assert external_binding.target == "Controller"
        assert external_binding.external_path == "external_values.ssv"
        assert external_binding.parameter_mapping is None

    with SSV(EXTERNAL_SSV_FIXTURE) as ssv:
        assert ssv.document.name == "ControllerExternal"
        assert len(ssv.parameters) == 1
        assert ssv.parameters[0].name == "gain"
        assert ssv.parameters[0].attributes["value"] == "0.8"
