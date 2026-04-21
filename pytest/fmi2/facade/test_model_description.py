from __future__ import annotations

import pytest

from pyssp_standard.md import ModelDescription


def test_exposes_core_variable_groups(model_description_fixture):
    with ModelDescription(model_description_fixture) as md:
        assert len(md.inputs) > 0
        assert len(md.outputs) > 0
        assert len(md.parameters) > 0


def test_get_filters_by_causality_and_variability(model_description_fixture):
    with ModelDescription(model_description_fixture) as md:
        no_matches = md.get("none", "none")
        matches_causality = md.get(causality="parameter")
        matches_variability = md.get(variability="tunable")
        matches_both = md.get("parameter", "tunable")

    assert len(no_matches) == 0
    assert len(matches_variability) >= len(matches_both)
    assert len(matches_causality) >= len(matches_both)


def test_requires_loading_before_access(model_description_fixture):
    md = ModelDescription(model_description_fixture)

    with pytest.raises(RuntimeError, match="not loaded"):
        _ = md.root


def test_can_be_loaded_from_xml_text(model_description_fixture):
    xml_text = model_description_fixture.read_text(encoding="utf-8")

    with ModelDescription(xml_text=xml_text) as md:
        assert md.root.tag == "fmiModelDescription"
        assert len(md.variables) > 0
        assert md.check_compliance() is True
