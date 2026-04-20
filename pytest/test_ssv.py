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
        file.__check_compliance__()


def test_check_ssp2_schema(ssv2_file):

    with SSV(ssv2_file) as file:
        assert file.version == "2.0"
        assert file.identifier == "ssv2"
        file.__check_compliance__()


def test_creation(write_file):

    with SSV(write_file, 'w') as file:
        file.add_parameter(parname='Cats', ptype='Integer', value=10)
        file.add_parameter(parname='Weight', ptype='Real', value=20.4, unit="kg")
        file.add_unit("kg", {"kg": 1})
        file.add_unit("N")
        file.__check_compliance__()


def test_creation_round_trip_preserves_units_and_metadata(write_file):

    with SSV(write_file, 'w') as file:
        file.top_level_metadata.author = "tester"
        file.base_element.description = "demo"
        file.add_parameter(parname='Weight', ptype='Real', value=20.4, unit="kg")
        file.add_unit("kg", {"kg": 1})

    with SSV(write_file) as file:
        assert file.metadata.author == "tester"
        assert file.metadata.description == "demo"
        assert len(file.units) == 1
        assert file.units[0].name == "kg"
        assert file.parameters[0].attributes["unit"] == "kg"
