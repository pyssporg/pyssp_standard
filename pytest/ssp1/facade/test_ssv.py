from __future__ import annotations

import pytest
from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model import Ssp1Annotation, Ssp1EnumerationItem, Ssp1Parameter
from pyssp_standard.ssv import SSV


def test_check_compliance_accepts_reference_fixture(external_ssv_fixture):
    with SSV(external_ssv_fixture) as ssv:
        assert ssv.check_compliance() is True


def test_create_round_trip_preserves_units_and_metadata(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.metadata.author = "tester"
        ssv.xml.metadata.description = "demo"
        ssv.xml.add_parameter(parname="Weight", ptype="Real", value=20.4, unit="kg")
        ssv.xml.add_unit("kg", {"kg": 1})

    with SSV(path) as ssv:
        assert ssv.xml.metadata.author == "tester"
        assert ssv.xml.metadata.description == "demo"
        assert len(ssv.xml.units) == 1
        assert ssv.xml.units[0].name == "kg"
        assert ssv.xml.parameters[0].attributes["unit"] == "kg"


def test_round_trip_preserves_supported_parameter_types(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.add_parameter(parname="real_param", ptype="Real", value=20.4, unit="kg")
        ssv.xml.add_parameter(parname="int_param", ptype="Integer", value=7)
        ssv.xml.add_parameter(parname="bool_param", ptype="Boolean", value=True)
        ssv.xml.add_parameter(parname="string_param", ptype="String", value="demo")
        ssv.xml.add_parameter(parname="enum_param", ptype="Enumeration", value="1", name="ON")
        ssv.xml.add_parameter(
            parname="binary_param",
            ptype="Binary",
            value="cafe",
            mimetype="application/octet-stream",
        )
        ssv.xml.add_unit("kg", {"kg": 1})

    with SSV(path) as ssv:
        params = {param.name: param for param in ssv.xml.parameters}

        assert params["real_param"].attributes == {"value": "20.4", "unit": "kg"}
        assert params["int_param"].attributes == {"value": "7"}
        assert params["bool_param"].attributes == {"value": "true"}
        assert params["string_param"].attributes == {"value": "demo"}
        assert params["enum_param"].attributes == {"value": "1", "name": "ON"}
        assert params["binary_param"].attributes == {
            "value": "cafe",
            "mime-type": "application/octet-stream",
        }


def test_extend_parameters_accepts_mappings_tuples_and_parameter_specs(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.extend_parameters(
            [
                ("gain", 3.5),
                Ssp1Parameter(name="enabled", type_name="Boolean", attributes={"value": "true"}),
                Ssp1Parameter(name="mode", type_name="Enumeration", attributes={"value": "1", "name": "ON"}),
            ]
        )
        ssv.xml.extend_parameters({"offset": -2, "label": "demo"})

    with SSV(path) as ssv:
        params = {param.name: param for param in ssv.xml.parameters}

        assert params["gain"].type_name == "Real"
        assert params["gain"].attributes == {"value": "3.5"}
        assert params["enabled"].type_name == "Boolean"
        assert params["enabled"].attributes == {"value": "true"}
        assert params["mode"].type_name == "Enumeration"
        assert params["mode"].attributes == {"value": "1", "name": "ON"}
        assert params["offset"].type_name == "Integer"
        assert params["offset"].attributes == {"value": "-2"}
        assert params["label"].type_name == "String"
        assert params["label"].attributes == {"value": "demo"}


def test_add_unit_reuses_existing_definition(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        first = ssv.xml.add_unit("kg", {"kg": 1})
        second = ssv.xml.add_unit("kg", {"kg": 1})

        assert first is second
        assert len(ssv.xml.units) == 1


def test_add_unit_rejects_conflicting_definition(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.add_unit("kg", {"kg": 1})

        with pytest.raises(ValueError, match="already exists with different definition"):
            ssv.xml.add_unit("kg", {"m": 1})


def test_compliance_accepts_builtin_bracket_unit(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.add_parameter(parname="distance", ptype="Real", value=1.2, unit="[m]")
        assert ssv.check_compliance() is True


def test_compliance_rejects_unknown_custom_unit(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.add_parameter(parname="distance", ptype="Real", value=1.2, unit="parsec")

        with pytest.raises(ValueError, match="references unknown unit 'parsec'"):
            ssv.check_compliance()


def test_external_fixture_loads_as_plain_standalone_document(external_ssv_fixture):
    with SSV(external_ssv_fixture) as ssv:
        assert ssv.xml.name == "ControllerExternal"
        assert len(ssv.xml.parameters) == 1
        assert ssv.xml.parameters[0].name == "gain"
        assert ssv.xml.parameters[0].attributes["value"] == "0.8"


def test_round_trip_preserves_metadata_parameter_and_unit_annotations(tmp_path):
    path = tmp_path / "annotations.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.metadata.annotations.append(
            Ssp1Annotation(
                type_name="com.example.doc",
                elements=[ET.fromstring('<doc xmlns="urn:test">top-level</doc>')],
            )
        )
        parameter = ssv.xml.add_parameter(parname="gain", ptype="Real", value=1.5, unit="kg")
        parameter.annotations.append(
            Ssp1Annotation(
                type_name="com.example.parameter",
                elements=[ET.fromstring('<hint xmlns="urn:test" priority="high">gain</hint>')],
            )
        )
        unit = ssv.xml.add_unit("kg", {"kg": 1})
        unit.annotations.append(
            Ssp1Annotation(
                type_name="com.example.unit",
                elements=[ET.fromstring('<unitNote xmlns="urn:test">mass</unitNote>')],
            )
        )

    with SSV(path) as ssv:
        assert ssv.xml.metadata.annotations[0].type_name == "com.example.doc"
        assert ssv.xml.metadata.annotations[0].elements[0].text == "top-level"
        assert ssv.xml.parameters[0].annotations[0].type_name == "com.example.parameter"
        assert ssv.xml.parameters[0].annotations[0].elements[0].attrib == {"priority": "high"}
        assert ssv.xml.units[0].annotations[0].type_name == "com.example.unit"
        assert ssv.xml.units[0].annotations[0].elements[0].tag == "{urn:test}unitNote"


def test_round_trip_preserves_enumerations(tmp_path):
    path = tmp_path / "enumerations.ssv"

    with SSV(path, "w") as ssv:
        enumeration = ssv.xml.add_enumeration(
            "AircraftState",
            [
                Ssp1EnumerationItem(name="OFF", value=0),
                Ssp1EnumerationItem(name="ON", value=1),
            ],
        )
        enumeration.annotations.append(
            Ssp1Annotation(
                type_name="com.example.enumeration",
                elements=[ET.fromstring('<note xmlns="urn:test">states</note>')],
            )
        )
        ssv.xml.add_parameter(parname="state", ptype="Enumeration", value="1", name="ON")

    with SSV(path) as ssv:
        assert len(ssv.xml.enumerations) == 1
        enumeration = ssv.xml.enumerations[0]
        assert enumeration.name == "AircraftState"
        assert [(item.name, item.value) for item in enumeration.items] == [("OFF", 0), ("ON", 1)]
        assert enumeration.annotations[0].elements[0].text == "states"
        assert ssv.xml.parameters[0].attributes == {"value": "1", "name": "ON"}


def test_round_trip_preserves_parameter_unit_and_enumeration_order_in_serialized_xml(tmp_path):
    path = tmp_path / "ordered.ssv"
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ssv:ParameterSet xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon" xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues" version="1.0" name="OrderedSet">
  <ssv:Parameters>
    <ssv:Parameter name="beta_param"><ssv:Real unit="kg" value="2.0" /></ssv:Parameter>
    <ssv:Parameter name="alpha_param"><ssv:Integer value="1" /></ssv:Parameter>
    <ssv:Parameter name="gamma_param"><ssv:Boolean value="true" /></ssv:Parameter>
  </ssv:Parameters>
  <ssv:Enumerations>
    <ssc:Enumeration name="SecondEnum"><ssc:Item value="2" name="TWO" /></ssc:Enumeration>
    <ssc:Enumeration name="FirstEnum"><ssc:Item name="ONE" value="1" /></ssc:Enumeration>
  </ssv:Enumerations>
  <ssv:Units>
    <ssc:Unit name="kg"><ssc:BaseUnit kg="1" /></ssc:Unit>
    <ssc:Unit name="m"><ssc:BaseUnit m="1" /></ssc:Unit>
  </ssv:Units>
</ssv:ParameterSet>
""",
        encoding="utf-8",
    )

    with SSV(path, "a"):
        pass

    with SSV(path) as ssv:
        assert [parameter.name for parameter in ssv.xml.parameters] == ["beta_param", "alpha_param", "gamma_param"]
        assert [unit.name for unit in ssv.xml.units] == ["kg", "m"]
        assert [enumeration.name for enumeration in ssv.xml.enumerations] == ["SecondEnum", "FirstEnum"]

    xml_text = path.read_text(encoding="utf-8")
    assert xml_text.index('name="beta_param"') < xml_text.index('name="alpha_param"')
    assert xml_text.index('name="alpha_param"') < xml_text.index('name="gamma_param"')
    assert xml_text.index('Unit name="kg"') < xml_text.index('Unit name="m"')
    assert xml_text.index('Enumeration name="SecondEnum"') < xml_text.index('Enumeration name="FirstEnum"')
