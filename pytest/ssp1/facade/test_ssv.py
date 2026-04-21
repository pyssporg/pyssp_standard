from __future__ import annotations

import pytest

from pyssp_standard.ssv import SSV


def test_check_compliance_accepts_reference_fixture(external_ssv_fixture):
    with SSV(external_ssv_fixture) as ssv:
        assert ssv.check_compliance() is True


def test_create_round_trip_preserves_units_and_metadata(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.metadata.author = "tester"
        ssv.metadata.description = "demo"
        ssv.add_parameter(parname="Weight", ptype="Real", value=20.4, unit="kg")
        ssv.add_unit("kg", {"kg": 1})

    with SSV(path) as ssv:
        assert ssv.metadata.author == "tester"
        assert ssv.metadata.description == "demo"
        assert len(ssv.units) == 1
        assert ssv.units[0].name == "kg"
        assert ssv.parameters[0].attributes["unit"] == "kg"


def test_round_trip_preserves_supported_parameter_types(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.add_parameter(parname="real_param", ptype="Real", value=20.4, unit="kg")
        ssv.add_parameter(parname="int_param", ptype="Integer", value=7)
        ssv.add_parameter(parname="bool_param", ptype="Boolean", value=True)
        ssv.add_parameter(parname="string_param", ptype="String", value="demo")
        ssv.add_parameter(parname="enum_param", ptype="Enumeration", value="1", name="ON")
        ssv.add_parameter(
            parname="binary_param",
            ptype="Binary",
            value="cafe",
            mimetype="application/octet-stream",
        )
        ssv.add_unit("kg", {"kg": 1})

    with SSV(path) as ssv:
        params = {param.name: param for param in ssv.parameters}

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
        first = ssv.add_unit("kg", {"kg": 1})
        second = ssv.add_unit("kg", {"kg": 1})

        assert first is second
        assert len(ssv.units) == 1


def test_add_unit_rejects_conflicting_definition(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.add_unit("kg", {"kg": 1})

        with pytest.raises(ValueError, match="already exists with different definition"):
            ssv.add_unit("kg", {"m": 1})


def test_compliance_accepts_builtin_bracket_unit(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.add_parameter(parname="distance", ptype="Real", value=1.2, unit="[m]")
        assert ssv.check_compliance() is True


def test_compliance_rejects_unknown_custom_unit(tmp_path):
    path = tmp_path / "test.ssv"

    with SSV(path, "w") as ssv:
        ssv.add_parameter(parname="distance", ptype="Real", value=1.2, unit="parsec")

        with pytest.raises(ValueError, match="references unknown unit 'parsec'"):
            ssv.check_compliance()


def test_external_fixture_loads_as_plain_standalone_document(external_ssv_fixture):
    with SSV(external_ssv_fixture) as ssv:
        assert ssv.document.name == "ControllerExternal"
        assert len(ssv.parameters) == 1
        assert ssv.parameters[0].name == "gain"
        assert ssv.parameters[0].attributes["value"] == "0.8"
