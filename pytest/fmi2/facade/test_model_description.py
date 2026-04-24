from __future__ import annotations

import pytest

from pyssp_standard.md import ModelDescription
from pyssp_standard.standard.fmi2.model import (
    Fmi2DefaultExperiment,
    Fmi2ModelStructure,
    Fmi2ScalarVariable,
    Fmi2TypeDefinition,
    Fmi2Unit,
    Fmi2Unknown,
)


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


def test_get_type_definitions_and_units_support_name_filters(model_description_fixture):
    with ModelDescription(model_description_fixture) as md:
        all_units = md.xml.get_units()
        named_units = md.xml.get_units("K")
        all_type_definitions = md.xml.get_type_definitions()
        enum_type_definitions = md.xml.get_type_definitions(type_name="Enumeration")

    assert len(all_units) > 0
    assert all(unit.name == "K" for unit in named_units)
    assert len(all_type_definitions) > 0
    assert all(type_definition.type_name == "Enumeration" for type_definition in enum_type_definitions)


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


def test_round_trip_preserves_metadata_and_repeated_element_order(tmp_path):
    path = tmp_path / "modelDescription.xml"
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription guid="{ordered-guid}" modelName="OrderedModel" fmiVersion="2.0" generationTool="pytest" generationDateAndTime="2026-04-22T12:00:00Z" variableNamingConvention="structured">
  <CoSimulation modelIdentifier="OrderedModel" />
  <UnitDefinitions>
    <Unit name="second"><BaseUnit s="1" /></Unit>
    <Unit name="meter"><BaseUnit m="1" /></Unit>
  </UnitDefinitions>
  <TypeDefinitions>
    <SimpleType name="SecondType"><Real quantity="time" /></SimpleType>
    <SimpleType name="FirstType"><Integer /></SimpleType>
  </TypeDefinitions>
  <ModelVariables>
    <ScalarVariable causality="input" valueReference="2" name="beta"><Real /></ScalarVariable>
    <ScalarVariable name="alpha" valueReference="1" causality="parameter"><Integer /></ScalarVariable>
    <ScalarVariable name="gamma" causality="output" valueReference="3"><Boolean /></ScalarVariable>
  </ModelVariables>
  <ModelStructure>
    <Outputs>
      <Unknown index="3" />
      <Unknown index="1" />
    </Outputs>
  </ModelStructure>
</fmiModelDescription>
""",
        encoding="utf-8",
    )

    with ModelDescription(path, mode="a"):
        pass

    with ModelDescription(path, mode="r") as md:
        assert md.xml.model_name == "OrderedModel"
        assert md.xml.guid == "{ordered-guid}"
        assert md.xml.generation_tool == "pytest"
        assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"
        assert md.xml.variable_naming_convention == "structured"
        assert md.xml.number_of_event_indicators is None
        assert md.xml.default_experiment is None
        assert [unit.name for unit in md.xml.unit_definitions] == ["second", "meter"]
        assert [type_definition.name for type_definition in md.xml.type_definitions] == ["SecondType", "FirstType"]
        assert [variable.name for variable in md.xml.variables] == ["beta", "alpha", "gamma"]
        assert [unknown.index for unknown in md.xml.model_structure.outputs] == ["3", "1"]

    xml_text = path.read_text(encoding="utf-8")
    assert xml_text.index("<CoSimulation") < xml_text.index("<UnitDefinitions>")
    assert xml_text.index("<UnitDefinitions>") < xml_text.index("<TypeDefinitions>")
    assert xml_text.index("<TypeDefinitions>") < xml_text.index("<ModelVariables>")
    assert xml_text.index('<Unit name="second"') < xml_text.index('<Unit name="meter"')
    assert xml_text.index('<SimpleType name="SecondType"') < xml_text.index('<SimpleType name="FirstType"')
    assert xml_text.index('<ScalarVariable name="beta"') < xml_text.index('<ScalarVariable name="alpha"')
    assert xml_text.index('<ScalarVariable name="alpha"') < xml_text.index('<ScalarVariable name="gamma"')
    assert xml_text.index('<Unknown index="3"') < xml_text.index('<Unknown index="1"')
