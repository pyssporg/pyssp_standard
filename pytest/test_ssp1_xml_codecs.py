from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from pyssp_standard.standard.ssp1.codec import Ssp1SsdXmlCodec, Ssp1SsmXmlCodec


SSD_FIXTURE = Path("pytest/doc/embrace/SystemStructure.ssd")
SSM_FIXTURE = Path("pytest/doc/embrace/resources/ECS_HW.ssm")


def test_ssp1_ssd_xml_codec_parses_fixture_root_metadata():
    document = Ssp1SsdXmlCodec().parse(SSD_FIXTURE.read_text(encoding="utf-8"))

    assert document.name == "embrace"
    assert document.version == "1.0"
    assert document.root.local_name == "SystemStructureDescription"
    assert any(child.local_name == "System" for child in document.root.children)


def test_ssp1_ssd_xml_codec_round_trips_fixture_structure():
    codec = Ssp1SsdXmlCodec()
    original = codec.parse(SSD_FIXTURE.read_text(encoding="utf-8"))

    xml_text = codec.serialize(original)
    reparsed = codec.parse(xml_text)

    assert reparsed.name == original.name
    assert reparsed.version == original.version
    assert [child.local_name for child in reparsed.root.children] == [
        child.local_name for child in original.root.children
    ]


def test_ssp1_ssm_xml_codec_parses_fixture_entries():
    document = Ssp1SsmXmlCodec().parse(SSM_FIXTURE.read_text(encoding="utf-8"))

    assert document.version == "1.0"
    assert document.root.local_name == "ParameterMapping"
    entries = [child for child in document.root.children if child.local_name == "MappingEntry"]
    assert len(entries) > 10
    assert entries[0].attributes["target"] == "ECS_HW.reqCoolingTemperature"


def test_ssp1_ssm_xml_codec_serializes_transformations():
    xml_text = """<ssm:ParameterMapping xmlns:ssm="http://ssp-standard.org/SSP1/SystemStructureParameterMapping" version="1.0"><ssm:MappingEntry source="a" target="b" suppressUnitConversion="true"><ssm:LinearTransformation factor="2" offset="0" /></ssm:MappingEntry></ssm:ParameterMapping>"""

    codec = Ssp1SsmXmlCodec()
    document = codec.parse(xml_text)
    rendered = codec.serialize(document)
    root = ET.fromstring(rendered)

    assert root.attrib["version"] == "1.0"
    entry = next(child for child in root if child.tag.endswith("MappingEntry"))
    assert entry.attrib["source"] == "a"
    transformation = next(child for child in entry if child.tag.endswith("LinearTransformation"))
    assert transformation.attrib == {"factor": "2", "offset": "0"}
