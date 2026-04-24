from __future__ import annotations

from pyssp_standard.standard.ssp1.codec import Ssp1SsdCodec
from pyssp_standard.standard.ssp1.model import (
    Ssd1Component,
    Ssd1ParameterBinding,
    Ssd1ParameterMappingReference,
    Ssd1System,
    Ssd1SystemStructureDescription,
)
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1Transformation
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping


def test_parses_embrace_fixture(embrace_ssd_fixture):
    document = Ssp1SsdCodec().parse(embrace_ssd_fixture.read_text(encoding="utf-8"))

    assert document.name == "embrace"
    assert document.version == "1.0"
    assert document.system is not None
    assert document.system.name == "root"
    assert len(document.system.elements) == 5
    assert len(document.system.connections) > 10


def test_parses_external_parameter_binding_and_mapping_references(embrace_ssd_fixture):
    document = Ssp1SsdCodec().parse(embrace_ssd_fixture.read_text(encoding="utf-8"))

    assert len(document.parameter_bindings) == 1
    binding = document.parameter_bindings[0]
    assert binding.source == "resources/RAPID_Systems_2021-03-29_Test_1.ssv"
    assert binding.parameter_mapping is not None
    assert binding.parameter_mapping.source == "resources/ECS_HW.ssm"
    assert binding.parameter_set is None
    assert binding.parameter_mapping.mapping is None


def test_round_trip_preserves_inline_and_external_parameter_bindings(mixed_ssd_fixture):
    codec = Ssp1SsdCodec()
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


def test_round_trip_preserves_inline_parameter_mapping_document():
    codec = Ssp1SsdCodec()
    mapping = Ssp1ParameterMapping(version="1.0")
    mapping.add_mapping(
        "source_gain",
        "Plant.gain",
        suppress_unit_conversion=True,
        transformation=Ssp1Transformation("LinearTransformation", {"factor": 2, "offset": 0}),
    )
    document = Ssd1SystemStructureDescription(
        name="InlineMapping",
        version="1.0",
        system=Ssd1System(
            name="system",
            parameter_bindings=[
                Ssd1ParameterBinding(
                    parameter_mapping=Ssd1ParameterMappingReference(mapping=mapping),
                )
            ],
        ),
    )

    reparsed = codec.parse(codec.serialize(document))

    assert reparsed.parameter_bindings[0].parameter_mapping is not None
    assert reparsed.parameter_bindings[0].parameter_mapping.source is None
    assert reparsed.parameter_bindings[0].parameter_mapping.mapping is not None
    assert reparsed.parameter_bindings[0].parameter_mapping.mapping.mappings[0].target == "Plant.gain"
    assert reparsed.parameter_bindings[0].parameter_mapping.mapping.mappings[0].suppress_unit_conversion is True


def test_round_trip_preserves_component_parameter_bindings():
    codec = Ssp1SsdCodec()
    document = Ssd1SystemStructureDescription(
        name="ComponentBindings",
        version="1.0",
        system=Ssd1System(
            name="system",
            elements=[
                Ssd1Component(
                    name="Plant",
                    source="resources/Plant.fmu",
                    parameter_bindings=[
                        Ssd1ParameterBinding(
                            parameter_set=Ssp1ParameterSet(
                                name="PlantInline",
                                version="1.0",
                                parameters=[
                                    Ssp1Parameter(name="gain", type_name="Real", attributes={"value": "1.5"})
                                ],
                            )
                        )
                    ],
                )
            ],
        ),
    )

    reparsed = codec.parse(codec.serialize(document))

    assert reparsed.system is not None
    assert len(reparsed.system.elements) == 1
    assert len(reparsed.system.elements[0].parameter_bindings) == 1
    assert reparsed.system.elements[0].parameter_bindings[0].parameter_set is not None
    assert reparsed.system.elements[0].parameter_bindings[0].parameter_set.parameters[0].name == "gain"
    assert reparsed.system.elements[0].parameter_bindings[0].parameter_set.parameters[0].attributes["value"] == "1.5"
