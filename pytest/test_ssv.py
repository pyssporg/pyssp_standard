import pytest
from pathlib import Path
from pyssp_standard.ssv import SSV


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace/resources/RAPID_Systems_2021-03-29_Test_1.ssv")


@pytest.fixture
def ssv2_file():
    return Path("pytest/doc/ssv2_ex.ssv")


@pytest.fixture
def write_file():
    test_file = Path('./test.ssv')
    yield test_file
    test_file.unlink()


def test_read_correct_file(read_file):  # Asserts that reading a known correct file does not raise an exception

    with SSV(read_file) as file:
        print(file)
        file.check_compliance()

def test_creation(write_file):

    with SSV(write_file, 'w') as file:
        file.add_parameter(parname='Cats', ptype='Integer', value=10)
        file.add_parameter(parname='Weight', ptype='Real', value=20.4, unit="kg")
        file.add_unit("kg", {"kg": 1})
        file.add_unit("N")
        file.check_compliance()


def test_creation_round_trip_preserves_units_and_metadata(write_file):

    with SSV(write_file, 'w') as file:
        file.metadata.author = "tester"
        file.metadata.description = "demo"
        file.add_parameter(parname='Weight', ptype='Real', value=20.4, unit="kg")
        file.add_unit("kg", {"kg": 1})

    with SSV(write_file) as file:
        assert file.metadata.author == "tester"
        assert file.metadata.description == "demo"
        assert len(file.units) == 1
        assert file.units[0].name == "kg"
        assert file.parameters[0].attributes["unit"] == "kg"


def test_round_trip_preserves_supported_parameter_types(write_file):

    with SSV(write_file, "w") as file:
        file.add_parameter(parname="real_param", ptype="Real", value=20.4, unit="kg")
        file.add_parameter(parname="int_param", ptype="Integer", value=7)
        file.add_parameter(parname="bool_param", ptype="Boolean", value=True)
        file.add_parameter(parname="string_param", ptype="String", value="demo")
        file.add_parameter(parname="enum_param", ptype="Enumeration", value="1", name="ON")
        file.add_parameter(
            parname="binary_param",
            ptype="Binary",
            value="cafe",
            mimetype="application/octet-stream",
        )
        file.add_unit("kg", {"kg": 1})

    with SSV(write_file) as file:
        params = {param.name: param for param in file.parameters}

        assert params["real_param"].attributes == {"value": "20.4", "unit": "kg"}
        assert params["int_param"].attributes == {"value": "7"}
        assert params["bool_param"].attributes == {"value": "true"}
        assert params["string_param"].attributes == {"value": "demo"}
        assert params["enum_param"].attributes == {"value": "1", "name": "ON"}
        assert params["binary_param"].attributes == {
            "value": "cafe",
            "mime-type": "application/octet-stream",
        }


def test_add_unit_reuses_existing_definition(write_file):

    with SSV(write_file, "w") as file:
        first = file.add_unit("kg", {"kg": 1})
        second = file.add_unit("kg", {"kg": 1})

        assert first is second
        assert len(file.units) == 1


def test_add_unit_rejects_conflicting_definition(write_file):

    with SSV(write_file, "w") as file:
        file.add_unit("kg", {"kg": 1})

        with pytest.raises(ValueError, match="already exists with different definition"):
            file.add_unit("kg", {"m": 1})


def test_compliance_accepts_builtin_bracket_unit(write_file):

    with SSV(write_file, "w") as file:
        file.add_parameter(parname="distance", ptype="Real", value=1.2, unit="[m]")
        assert file.check_compliance() is True


def test_compliance_rejects_unknown_custom_unit(write_file):

    with SSV(write_file, "w") as file:
        file.add_parameter(parname="distance", ptype="Real", value=1.2, unit="parsec")

        with pytest.raises(ValueError, match="references unknown unit 'parsec'"):
            file.check_compliance()
