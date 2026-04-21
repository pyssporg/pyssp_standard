import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from pyssp_standard.ssm import SSM, Ssp1Transformation
from pyssp_standard.standard.ssp1.codec.ssm_xml_codec import NS_SSC, NS_SSM


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace/resources/ECS_HW.ssm")


@pytest.fixture
def write_file():
    test_file = Path("./test.ssm")
    yield test_file
    test_file.unlink()


def test_read_correct_file(read_file):  # Asserts that reading a known correct file does not raise an exception

    with SSM(read_file) as file:
        print(file)
        file.check_compliance()


def test_create_and_edit_basic_file(write_file):

    with SSM(write_file, 'w') as f:
        f.add_mapping('dog', 'shepard')
        f.add_mapping('cat', 'odd', transformation=Ssp1Transformation('LinearTransformation', {'factor': 2, 'offset': 0}))
        f.check_compliance()

    with SSM(write_file, 'a') as f:
        f.edit_mapping(target='shepard', source='tax', suppress_unit_conversion=True)
        f.check_compliance()


def test_transformation_xml_is_constructed_by_codec(write_file):
    with SSM(write_file, 'w') as f:
        f.add_mapping(
            'cat',
            'odd',
            transformation=Ssp1Transformation('LinearTransformation', {'factor': 1, 'offset': 0}),
        )

    root = ET.parse(write_file).getroot()
    assert root.tag == f"{{{NS_SSM}}}ParameterMapping"
    entry = next(child for child in root if child.tag == f"{{{NS_SSM}}}MappingEntry")
    transformation = next(child for child in entry)
    assert transformation.tag == f"{{{NS_SSC}}}LinearTransformation"
    assert transformation.attrib == {'factor': '1', 'offset': '0'}
