from __future__ import annotations

import pytest

from pyssp_standard.md import ModelDescription


def test_exposes_core_variable_groups(model_description_fixture):
    with ModelDescription(model_description_fixture) as md:
        assert len(md.xml.inputs) > 0
        assert len(md.xml.outputs) > 0
        assert len(md.xml.parameters) > 0


def test_get_filters_by_causality_and_variability(model_description_fixture):
    with ModelDescription(model_description_fixture) as md:
        no_matches = md.xml.get("none", "none")
        matches_causality = md.xml.get(causality="parameter")
        matches_variability = md.xml.get(variability="tunable")
        matches_both = md.xml.get("parameter", "tunable")

    assert len(no_matches) == 0
    assert len(matches_variability) >= len(matches_both)
    assert len(matches_causality) >= len(matches_both)


def test_requires_loading_before_access(model_description_fixture):
    md = ModelDescription(model_description_fixture)

    with pytest.raises(RuntimeError, match="not loaded"):
        _ = md.xml


def test_can_be_loaded_from_xml_text(model_description_fixture):
    xml_text = model_description_fixture.read_text(encoding="utf-8")

    with ModelDescription("model_description.xml") as md:
        md.from_xml(xml_text)
        assert md.xml.root.tag == "fmiModelDescription"
        assert len(md.xml.variables) > 0
        assert md.check_compliance() is True
