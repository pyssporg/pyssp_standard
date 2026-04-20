from pathlib import Path

import pytest

from pyssp_standard.fmu import ModelDescription


@pytest.fixture
def md_file():
    return Path("pytest/doc/embrace/fmu/modelDescription.xml")


def test_model_description_exposes_core_variable_groups(md_file):
    with ModelDescription(md_file) as md:
        inputs = md.inputs
        outputs = md.outputs
        parameters = md.parameters

    assert len(inputs) > 0
    assert len(outputs) > 0
    assert len(parameters) > 0


def test_model_description_get_filters_by_causality_and_variability(md_file):
    with ModelDescription(md_file) as md:
        no_matches = md.get("none", "none")
        matches_causality = md.get(causality="parameter")
        matches_variability = md.get(variability="tunable")
        matches_both = md.get("parameter", "tunable")

    assert len(no_matches) == 0
    assert len(matches_variability) >= len(matches_both)
    assert len(matches_causality) >= len(matches_both)


def test_model_description_requires_loading_before_access(md_file):
    md = ModelDescription(md_file)

    with pytest.raises(RuntimeError, match="not loaded"):
        _ = md.root


def test_model_description_can_be_loaded_from_xml_text(md_file):
    xml_text = md_file.read_text(encoding="utf-8")

    with ModelDescription(xml_text=xml_text) as md:
        assert md.root.tag == "fmiModelDescription"
        assert len(md.variables) > 0
