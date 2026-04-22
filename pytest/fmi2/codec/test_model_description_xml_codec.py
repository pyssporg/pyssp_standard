from __future__ import annotations

from pyssp_standard.md import ModelDescription
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import (
    Fmi2ElementInfo,
    Fmi2ModelDescriptionDocument,
    Fmi2ScalarVariable,
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
