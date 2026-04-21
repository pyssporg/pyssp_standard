from __future__ import annotations

from pyssp_standard.md import ModelDescription
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec


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

    with ModelDescription(xml_text=rendered) as md:
        assert md.check_compliance() is True
        assert len(md.variables) == len(document.variables)
        assert len(md.type_definitions) == len(document.type_definitions)
        assert len(md.document.model_structure.outputs) == len(document.model_structure.outputs)
