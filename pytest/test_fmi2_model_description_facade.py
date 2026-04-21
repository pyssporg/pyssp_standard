from __future__ import annotations

import shutil
from pathlib import Path

from pyssp_standard.fmu import FMU, ModelDescription
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec


MODEL_DESCRIPTION_FIXTURE = Path("pytest/doc/embrace/fmu/modelDescription.xml")
FMU_FIXTURE = Path("pytest/doc/embrace/resources/0001_ECS_HW.fmu")


def test_fmi2_codec_parses_fixture():
    document = Fmi2ModelDescriptionXmlCodec().parse(MODEL_DESCRIPTION_FIXTURE.read_text(encoding="utf-8"))

    assert document.root.tag == "fmiModelDescription"
    assert document.fmi_version == "2.0"
    assert document.interface_type == "CoSimulation"
    assert len(document.variables) > 0
    assert len(document.type_definitions) > 0
    assert len(document.model_structure.derivatives) > 0


def test_fmi2_codec_round_trips_schema_valid_fixture():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = MODEL_DESCRIPTION_FIXTURE.read_text(encoding="utf-8")

    document = codec.parse(xml_text)
    rendered = codec.serialize(document)

    with ModelDescription(xml_text=rendered) as md:
        md.check_compliance()
        assert len(md.variables) == len(document.variables)
        assert len(md.type_definitions) == len(document.type_definitions)
        assert len(md.document.model_structure.outputs) == len(document.model_structure.outputs)


def test_model_description_facade_exposes_core_variable_groups():
    with ModelDescription(MODEL_DESCRIPTION_FIXTURE) as md:
        assert len(md.inputs) > 0
        assert len(md.outputs) > 0
        assert len(md.parameters) > 0


def test_model_description_can_be_loaded_from_xml_text():
    xml_text = MODEL_DESCRIPTION_FIXTURE.read_text(encoding="utf-8")

    with ModelDescription(xml_text=xml_text) as md:
        assert md.root.tag == "fmiModelDescription"
        assert len(md.variables) > 0
        md.check_compliance()


def test_fmu_exposes_loaded_model_description_via_public_property(tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(FMU_FIXTURE, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        with fmu.model_description as md:
            assert md is not None
            assert len(md.inputs) > 0
            md.check_compliance()
