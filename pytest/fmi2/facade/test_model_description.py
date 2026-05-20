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

# ---------------------------------------------------------------------------
# strip_model_exchange test data
# ---------------------------------------------------------------------------

_ME_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription
  fmiVersion="2.0"
  modelName="TestME"
  guid="{test-guid}"
  numberOfEventIndicators="2">
  <ModelExchange
    modelIdentifier="TestME"
    completedIntegratorStepNotNeeded="true"
    needsExecutionTool="true"
    canGetAndSetFMUstate="true"
    providesDirectionalDerivative="true"/>
  <ModelVariables>
    <ScalarVariable name="u" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure>
    <Outputs><Unknown index="1"/></Outputs>
    <Derivatives><Unknown index="1"/></Derivatives>
  </ModelStructure>
</fmiModelDescription>"""

_CS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription
  fmiVersion="2.0"
  modelName="TestME"
  guid="{test-guid}"
  numberOfEventIndicators="2">
  <CoSimulation
    modelIdentifier="TestME"
    canGetAndSetFMUstate="true"
    providesDirectionalDerivative="true"/>
  <ModelVariables>
    <ScalarVariable name="u" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure>
    <Outputs><Unknown index="1"/></Outputs>
    <Derivatives><Unknown index="1"/></Derivatives>
  </ModelStructure>
</fmiModelDescription>"""


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

# ---------------------------------------------------------------------------
# strip_model_exchange tests
# ---------------------------------------------------------------------------


def test_strip_model_exchange_converts_type():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        md.strip_model_exchange()
        assert md.xml.interface_type == "CoSimulation"


def test_strip_model_exchange_removes_me_only_attributes():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        md.strip_model_exchange()
        assert "completedIntegratorStepNotNeeded" not in md.xml.interface_attributes
        assert "needsExecutionTool" not in md.xml.interface_attributes


def test_strip_model_exchange_preserves_shared_attributes():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        md.strip_model_exchange()
        assert md.xml.interface_attributes.get("modelIdentifier") == "TestME"
        assert md.xml.interface_attributes.get("canGetAndSetFMUstate") == "true"
        assert md.xml.interface_attributes.get("providesDirectionalDerivative") == "true"


def test_strip_model_exchange_clears_derivatives():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        md.strip_model_exchange()
        assert md.xml.model_structure.derivatives == []


def test_strip_model_exchange_clears_number_of_event_indicators():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        assert md.xml.number_of_event_indicators == 2
        md.strip_model_exchange()
        assert md.xml.number_of_event_indicators is None


def test_strip_model_exchange_passes_compliance():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        md.strip_model_exchange()
        assert md.check_compliance() is True


def test_strip_model_exchange_noop_when_already_cs():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_CS_XML)
        original_attrs = dict(md.xml.interface_attributes)
        original_derivatives = list(md.xml.model_structure.derivatives)
        original_nei = md.xml.number_of_event_indicators
        original_type = md.xml.interface_type

        md.strip_model_exchange()

        assert md.xml.interface_type == original_type
        assert md.xml.interface_attributes == original_attrs
        assert md.xml.model_structure.derivatives == original_derivatives
        assert md.xml.number_of_event_indicators == original_nei


def test_strip_model_exchange_noop_when_interface_none():
    """Construct a document with interface_type=None (no <ModelExchange> or <CoSimulation>)."""
    with ModelDescription("model_description.xml") as md:
        md.from_xml(
            """<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="NoneType" guid="{none-guid}">
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure/>
</fmiModelDescription>"""
        )
        assert md.xml.interface_type is None
        md.strip_model_exchange()
        assert md.xml.interface_type is None


def test_strip_model_exchange_idempotent():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        md.strip_model_exchange()
        first_attrs = dict(md.xml.interface_attributes)
        first_nei = md.xml.number_of_event_indicators
        first_derivatives = list(md.xml.model_structure.derivatives)

        md.strip_model_exchange()

        assert md.xml.interface_attributes == first_attrs
        assert md.xml.number_of_event_indicators == first_nei
        assert md.xml.model_structure.derivatives == first_derivatives


def test_strip_model_exchange_preserves_outputs_and_initial_unknowns():
    with ModelDescription("model_description.xml") as md:
        md.from_xml(_ME_XML)
        original_outputs = list(md.xml.model_structure.outputs)
        original_initial = list(md.xml.model_structure.initial_unknowns)
        md.strip_model_exchange()
        assert md.xml.model_structure.outputs == original_outputs
        assert md.xml.model_structure.initial_unknowns == original_initial


def test_strip_model_exchange_fails_when_not_loaded():
    md = ModelDescription("model_description.xml")
    with pytest.raises(RuntimeError, match="not loaded"):
        md.strip_model_exchange()
