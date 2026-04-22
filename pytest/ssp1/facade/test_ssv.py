from __future__ import annotations

import pytest
from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model import Ssp1Annotation, Ssp1EnumerationItem
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
