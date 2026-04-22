from __future__ import annotations

from pyssp_standard.standard.ssp1.codec import Ssp1SsdXmlCodec


def test_parses_embrace_fixture(embrace_ssd_fixture):
    document = Ssp1SsdXmlCodec().parse(embrace_ssd_fixture.read_text(encoding="utf-8"))

    assert document.name == "embrace"
    assert document.version == "1.0"
    assert document.system is not None
    assert document.system.name == "root"
    assert len(document.system.elements) == 5
    assert len(document.system.connections) > 10


def test_parses_external_parameter_binding_and_mapping_references(embrace_ssd_fixture):
    document = Ssp1SsdXmlCodec().parse(embrace_ssd_fixture.read_text(encoding="utf-8"))

    assert len(document.parameter_bindings) == 1
    binding = document.parameter_bindings[0]
    assert binding.source == "resources/RAPID_Systems_2021-03-29_Test_1.ssv"
    assert binding.parameter_mapping is not None
    assert binding.parameter_mapping.source == "resources/ECS_HW.ssm"
    assert binding.parameter_set is None
    assert binding.parameter_mapping.mapping is None


def test_round_trip_preserves_inline_and_external_parameter_bindings(mixed_ssd_fixture):
    codec = Ssp1SsdXmlCodec()
    document = codec.parse(mixed_ssd_fixture.read_text(encoding="utf-8"))

    assert len(document.parameter_bindings) == 2

    inline_binding = document.parameter_bindings[0]
    assert inline_binding.prefix == "Plant"
    assert inline_binding.source is None
    assert inline_binding.parameter_set is not None
    assert inline_binding.parameter_set.name == "PlantInline"
    assert inline_binding.parameter_set.parameters[0].name == "gain"
    assert inline_binding.parameter_set.parameters[0].attributes["value"] == "1.5"

    external_binding = document.parameter_bindings[1]
    assert external_binding.prefix == "Controller"
    assert external_binding.source == "external_values.ssv"
    assert external_binding.parameter_set is None

    reparsed = codec.parse(codec.serialize(document))
    assert len(reparsed.parameter_bindings) == 2
    assert reparsed.parameter_bindings[0].parameter_set is not None
    assert reparsed.parameter_bindings[0].parameter_set.parameters[0].attributes["value"] == "1.5"
    assert reparsed.parameter_bindings[1].source == "external_values.ssv"
