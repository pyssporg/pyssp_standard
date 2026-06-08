from __future__ import annotations

import pytest

from pyssp_standard.md import ModelDescription
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import (
    Fmi2ElementInfo,
    Fmi2InterfaceAttributes,
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
        capabilities=Fmi2InterfaceAttributes(model_identifier="MinimalME"),
        variables=[
            Fmi2ScalarVariable(
                name="u",
                value_reference=1,
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
        capabilities=Fmi2InterfaceAttributes(
            model_identifier="RoundTripME",
            completed_integrator_step_not_needed=True,
            can_get_and_set_fmu_state=True,
        ),
        number_of_event_indicators=4,
        variables=[Fmi2ScalarVariable(name="y", value_reference=1, type_name="Real")],
        model_structure=Fmi2ModelStructure(
            outputs=[Fmi2Unknown(index=1)],
            derivatives=[Fmi2Unknown(index=1)],
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
    assert reparsed.capabilities.completed_integrator_step_not_needed is False
    assert reparsed.capabilities.model_identifier == "RoundTripME"
    assert reparsed.capabilities.can_get_and_set_fmu_state is True
    assert reparsed.number_of_event_indicators is None
    assert reparsed.model_structure.derivatives == []
    assert len(reparsed.model_structure.outputs) == 1
    assert reparsed.model_structure.outputs[0].index == 1
    assert len(reparsed.variables) == 1
    assert reparsed.variables[0].name == "y"


# ---------------------------------------------------------------------------
# IMP-020: Edge-case tests for type corrections
# ---------------------------------------------------------------------------


def test_start_field_parses_float_for_real_types():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="StartTest" guid="{start-guid}">
  <CoSimulation modelIdentifier="StartTest" />
  <ModelVariables>
    <ScalarVariable name="r" valueReference="1"><Real start="1.5"/></ScalarVariable>
    <ScalarVariable name="i" valueReference="2"><Integer start="42"/></ScalarVariable>
    <ScalarVariable name="s" valueReference="3"><String start="hello"/></ScalarVariable>
    <ScalarVariable name="no" valueReference="4"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""
    document = codec.parse(xml_text)

    assert document.variables[0].start == 1.5  # float
    assert isinstance(document.variables[0].start, float)
    assert document.variables[1].start == 42  # integer → int
    assert isinstance(document.variables[1].start, int)
    assert document.variables[2].start == "hello"  # non-numeric → str
    assert isinstance(document.variables[2].start, str)
    assert document.variables[3].start is None


def test_unit_field_extracted_from_type_attributes():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="UnitTest" guid="{unit-guid}">
  <CoSimulation modelIdentifier="UnitTest" />
  <ModelVariables>
    <ScalarVariable name="v" valueReference="1"><Real unit="N" start="0.0"/></ScalarVariable>
    <ScalarVariable name="w" valueReference="2"><Integer unit="N"/></ScalarVariable>
    <ScalarVariable name="x" valueReference="3"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""
    document = codec.parse(xml_text)

    assert document.variables[0].unit == "N"
    assert document.variables[1].unit == "N"
    assert document.variables[2].unit is None


def test_dependencies_parsing_edge_cases():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="DepTest" guid="{dep-guid}">
  <CoSimulation modelIdentifier="DepTest" />
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure>
    <Outputs>
      <Unknown index="1" dependencies="3" />
      <Unknown index="2" dependencies="1 2 3" dependenciesKind="dependent constant" />
      <Unknown index="3" />
      <Unknown index="4" dependencies="" />
    </Outputs>
  </ModelStructure>
</fmiModelDescription>"""
    document = codec.parse(xml_text)

    outs = document.model_structure.outputs
    assert outs[0].dependencies == [3]
    assert outs[1].dependencies == [1, 2, 3]
    assert outs[1].dependencies_kind == ["dependent", "constant"]
    assert outs[2].dependencies == []  # absent
    assert outs[3].dependencies == []  # empty string


def test_round_trip_preserves_typed_values():
    codec = Fmi2ModelDescriptionXmlCodec()
    doc = Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version="2.0",
        model_name="TypeRoundTrip",
        guid="{type-rt-guid}",
        capabilities=Fmi2InterfaceAttributes(model_identifier="TypeRoundTrip"),
        variables=[
            Fmi2ScalarVariable(
                name="r", value_reference=10, type_name="Real",
                start=1.5, unit="N",
            ),
            Fmi2ScalarVariable(
                name="s", value_reference=20, type_name="Integer",
                start=42,
            ),
            Fmi2ScalarVariable(
                name="e", value_reference=30, type_name="Enumeration",
                start='"option_a"',
            ),
        ],
        model_structure=Fmi2ModelStructure(
            outputs=[
                Fmi2Unknown(index=10, dependencies=[1, 2], dependencies_kind=["dependent", "constant"]),
                Fmi2Unknown(index=20),
            ],
        ),
    )

    rendered = codec.serialize(doc)
    reparsed = codec.parse(rendered)

    assert reparsed.variables[0].value_reference == 10
    assert reparsed.variables[0].start == 1.5
    assert reparsed.variables[0].unit == "N"
    assert reparsed.variables[1].value_reference == 20
    assert reparsed.variables[1].start == 42
    assert reparsed.variables[2].value_reference == 30
    assert reparsed.variables[2].start == '"option_a"'
    assert reparsed.model_structure.outputs[0].index == 10
    assert reparsed.model_structure.outputs[0].dependencies == [1, 2]
    assert reparsed.model_structure.outputs[0].dependencies_kind == ["dependent", "constant"]
    assert reparsed.model_structure.outputs[1].index == 20
    assert reparsed.model_structure.outputs[1].dependencies == []


# ---------------------------------------------------------------------------
# IMP-021: Metadata completeness tests
# ---------------------------------------------------------------------------


def test_metadata_round_trip_preserves_description_author_version():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription
  fmiVersion="2.0"
  modelName="MetaTest"
  guid="{meta-guid}"
  description="Test model description"
  author="Test Author"
  version="1.0.0"
  generationTool="pytest"
  generationDateAndTime="2026-01-01T00:00:00Z"
  variableNamingConvention="structured">
  <CoSimulation modelIdentifier="MetaTest" />
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""
    document = codec.parse(xml_text)

    assert document.description == "Test model description"
    assert document.author == "Test Author"
    assert document.version == "1.0.0"
    assert document.generation_tool == "pytest"
    assert document.generation_date_and_time == "2026-01-01T00:00:00Z"
    assert document.variable_naming_convention == "structured"

    rendered = codec.serialize(document)
    reparsed = codec.parse(rendered)

    assert reparsed.description == "Test model description"
    assert reparsed.author == "Test Author"
    assert reparsed.version == "1.0.0"
    assert reparsed.generation_tool == "pytest"
    assert reparsed.generation_date_and_time == "2026-01-01T00:00:00Z"
    assert reparsed.variable_naming_convention == "structured"


def test_metadata_absent_fields_default_to_none():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="MinMeta" guid="{min-meta-guid}">
  <CoSimulation modelIdentifier="MinMeta" />
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""
    document = codec.parse(xml_text)

    assert document.description is None
    assert document.author is None
    assert document.version is None


def test_capabilities_typed_parsing():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="CapsTest" guid="{caps-guid}">
  <ModelExchange
    modelIdentifier="CapsTest"
    canGetAndSetFMUstate="true"
    canSerializeFMUstate="true"
    providesDirectionalDerivative="true"
    needsExecutionTool="true"
    completedIntegratorStepNotNeeded="true"
    someCustomAttr="custom"/>
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""
    document = codec.parse(xml_text)

    assert document.capabilities is not None
    assert document.capabilities.model_identifier == "CapsTest"
    assert document.capabilities.can_get_and_set_fmu_state is True
    assert document.capabilities.can_serialize_fmu_state is True
    assert document.capabilities.provides_directional_derivative is True
    assert document.capabilities.needs_execution_tool is True
    assert document.capabilities.completed_integrator_step_not_needed is True
    assert document.capabilities.can_be_instantiated_only_once_per_process is False
    assert document.capabilities.can_not_use_memory_management_functions is False
    assert document.capabilities.extra_attributes.get("someCustomAttr") == "custom"

    # Round-trip
    rendered = codec.serialize(document)
    reparsed = codec.parse(rendered)
    assert reparsed.capabilities.model_identifier == "CapsTest"
    assert reparsed.capabilities.can_get_and_set_fmu_state is True
    assert reparsed.capabilities.can_serialize_fmu_state is True
    assert reparsed.capabilities.provides_directional_derivative is True
    assert reparsed.capabilities.needs_execution_tool is True
    assert reparsed.capabilities.completed_integrator_step_not_needed is True
    assert reparsed.capabilities.can_be_instantiated_only_once_per_process is False


def test_capabilities_absent_when_no_interface_element():
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="NoIface" guid="{no-iface-guid}">
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""
    document = codec.parse(xml_text)
    assert document.capabilities is None
    assert document.interface_type is None


def test_capabilities_false_booleans_default():
    """Boolean attributes absent or 'false' should be False."""
    codec = Fmi2ModelDescriptionXmlCodec()
    xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="BoolTest" guid="{bool-guid}">
  <CoSimulation
    modelIdentifier="BoolTest"
    canGetAndSetFMUstate="false"
    canSerializeFMUstate="false"/>
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""
    document = codec.parse(xml_text)
    assert document.capabilities.can_get_and_set_fmu_state is False
    assert document.capabilities.can_serialize_fmu_state is False
    assert document.capabilities.provides_directional_derivative is False  # absent -> False
