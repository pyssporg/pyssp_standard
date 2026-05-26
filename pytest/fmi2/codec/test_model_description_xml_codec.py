from __future__ import annotations

import pytest

from pyssp_standard.md import ModelDescription
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import (
    Fmi2ElementInfo,
    Fmi2ModelDescriptionDocument,
    Fmi2ModelStructure,
    Fmi2ScalarVariable,
    Fmi2Unknown,
)


def test_parses_fixture(model_description_fixture):
    document = Fmi2ModelDescriptionXmlCodec().parse(model_description_fixture.read_text(encoding="utf-8"))

    assert document.root.tag == "fmiModelDescription"
    assert document.fmi_version == "2.0"
    assert document.interface_type == "CoSimulation"
    assert len(document.variables) > 0
    assert len(document.type_definitions) > 0
    assert len(document.model_structure.derivatives) > 0


def test_round_trip_preserves_schema_valid_fixture(model_description_fixture):
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = model_description_fixture.read_text(encoding="utf-8")

    document = codec.parse(xml_text)
    rendered = codec.serialize(document)

    with ModelDescription("model_description.xml") as md:
        md.from_xml(rendered)
        assert md.check_compliance() is True
        assert len(md.xml.variables) == len(document.variables)
        assert len(md.xml.type_definitions) == len(document.type_definitions)
        assert len(md.xml.model_structure.outputs) == len(document.model_structure.outputs)


def test_round_trip_supports_model_exchange_without_optional_sections():
    codec = Fmi2ModelDescriptionXmlCodec()
    document = Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version="2.0",
        model_name="MinimalME",
        guid="{test-guid}",
        interface_type="ModelExchange",
        interface_attributes={"modelIdentifier": "MinimalME"},
        variables=[
            Fmi2ScalarVariable(
                name="u",
                value_reference="1",
                type_name="Real",
            )
        ],
    )

    rendered = codec.serialize(document)
    reparsed = codec.parse(rendered)

    with ModelDescription("model_description.xml") as md:
        md.from_xml(rendered)
        assert md.check_compliance() is True

    assert reparsed.interface_type == "ModelExchange"
    assert reparsed.unit_definitions == []
    assert reparsed.type_definitions == []
    assert reparsed.default_experiment is None
    assert reparsed.model_structure.outputs == []
    assert reparsed.variables[0].name == "u"


def test_parses_fmi_unit_definitions_base_units_from_raw_xml():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="UnitModel" guid="{unit-guid}">
  <CoSimulation modelIdentifier="UnitModel" />
  <UnitDefinitions>
    <Unit name="V">
      <BaseUnit kg="1" m="2" s="-3" A="-1" />
    </Unit>
  </UnitDefinitions>
  <ModelVariables>
    <ScalarVariable name="u" valueReference="1">
      <Real />
    </ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>
"""

    document = codec.parse(xml_text)

    assert len(document.unit_definitions) == 1
    unit = document.unit_definitions[0]
    assert unit.name == "V"
    assert unit.base_unit == {"kg": "1", "m": "2", "s": "-3", "A": "-1"}


def test_strip_model_exchange_codec_round_trip():
    """Serialise after strip_model_exchange, re-parse, verify CS-only document."""
    codec = Fmi2ModelDescriptionXmlCodec()
    doc = Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version="2.0",
        model_name="RoundTripME",
        guid="{roundtrip-guid}",
        interface_type="ModelExchange",
        interface_attributes={
            "modelIdentifier": "RoundTripME",
            "completedIntegratorStepNotNeeded": "true",
            "canGetAndSetFMUstate": "true",
        },
        number_of_event_indicators=4,
        variables=[Fmi2ScalarVariable(name="y", value_reference="1", type_name="Real")],
        model_structure=Fmi2ModelStructure(
            outputs=[Fmi2Unknown(index="1")],
            derivatives=[Fmi2Unknown(index="1")],
        ),
    )

    me_xml = codec.serialize(doc)

    from pyssp_standard.md import ModelDescription
    with ModelDescription("model_description.xml") as md:
        md.from_xml(me_xml)
        md.strip_model_exchange()
        stripped_xml = codec.serialize(md.xml)

    reparsed = codec.parse(stripped_xml)

    assert reparsed.guid == "{roundtrip-guid}"
    assert reparsed.interface_type == "CoSimulation"
    assert "completedIntegratorStepNotNeeded" not in reparsed.interface_attributes
    assert reparsed.interface_attributes.get("modelIdentifier") == "RoundTripME"
    assert reparsed.interface_attributes.get("canGetAndSetFMUstate") == "true"
    assert reparsed.number_of_event_indicators is None
    assert reparsed.model_structure.derivatives == []
    assert len(reparsed.model_structure.outputs) == 1
    assert reparsed.model_structure.outputs[0].index == "1"
    assert len(reparsed.variables) == 1
    assert reparsed.variables[0].name == "y"
