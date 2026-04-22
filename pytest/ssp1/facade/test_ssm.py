from __future__ import annotations

import xml.etree.ElementTree as ET

from pyssp_standard.ssm import SSM, Ssp1Transformation
from pyssp_standard.standard.ssp1.codec.ssm_codec import NS_SSC, NS_SSM


def test_check_compliance_accepts_reference_fixture(embrace_ssm_fixture):
    with SSM(embrace_ssm_fixture) as ssm:
        assert ssm.check_compliance() is True
        assert len(ssm.mappings) == 203


def test_create_and_edit_round_trip(tmp_path):
    path = tmp_path / "test.ssm"

    with SSM(path, "w") as ssm:
        ssm.add_mapping("dog", "shepard")
        ssm.add_mapping(
            "cat",
            "odd",
            transformation=Ssp1Transformation("LinearTransformation", {"factor": 2, "offset": 0}),
        )
        assert ssm.check_compliance() is True

    with SSM(path, "a") as ssm:
        ssm.edit_mapping(target="shepard", source="tax", suppress_unit_conversion=True)
        assert ssm.check_compliance() is True

    with SSM(path) as ssm:
        assert len(ssm.mappings) == 2
        assert ssm.mappings[0].source == "tax"
        assert ssm.mappings[0].suppress_unit_conversion is True
        assert ssm.mappings[1].transformation is not None
        assert ssm.mappings[1].transformation.type_name == "LinearTransformation"


def test_codec_constructs_transformation_xml(tmp_path):
    path = tmp_path / "test.ssm"

    with SSM(path, "w") as ssm:
        ssm.add_mapping(
            "cat",
            "odd",
            transformation=Ssp1Transformation("LinearTransformation", {"factor": 1, "offset": 0}),
        )

    root = ET.parse(path).getroot()
    assert root.tag == f"{{{NS_SSM}}}ParameterMapping"
    entry = next(child for child in root if child.tag == f"{{{NS_SSM}}}MappingEntry")
    transformation = next(child for child in entry)
    assert transformation.tag == f"{{{NS_SSC}}}LinearTransformation"
    assert transformation.attrib == {"factor": "1", "offset": "0"}
