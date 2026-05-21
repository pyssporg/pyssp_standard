"""SSV facade tests for SSP2 (version 2.0) documents."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyssp_standard.standard.ssp2.model.ssv_model import Ssp2Dimension
from pyssp_standard.ssv import SSV


def test_read_ssp2_fixture_auto_detects_version(ssv2_fixture: Path):
    """R8: Read SSP2 fixture through SSV facade with auto-detected version."""
    with SSV(ssv2_fixture) as ssv:
        assert ssv.xml.version == "2.0"
        assert ssv.xml.name == "Example"
        assert len(ssv.xml.parameters) == 3
        # Verify Ssp2Parameter has dimensions
        assert ssv.xml.parameters[0].name == "example"
        assert len(ssv.xml.parameters[0].dimensions) == 2
        assert ssv.xml.parameters[0].dimensions[0].size == 3
        assert ssv.xml.parameters[0].dimensions[1].size == 2


def test_create_ssp2_document_round_trip(tmp_path: Path):
    """R9/R10: Create SSP2 document, write, read back, verify version."""
    path = tmp_path / "test_ssp2.ssv"

    with SSV(path, "w", version="2.0") as ssv:
        ssv.xml.add_parameter(parname="test_param", ptype="Real", value=1.5)

    # R10: Serialized XML must contain version="2.0"
    xml_text = path.read_text(encoding="utf-8")
    assert 'version="2.0"' in xml_text

    # R9: Read back and verify round-trip
    with SSV(path) as ssv:
        assert ssv.xml.version == "2.0"
        assert len(ssv.xml.parameters) == 1
        assert ssv.xml.parameters[0].name == "test_param"


def test_create_ssp2_document_with_dimensions(tmp_path: Path):
    """Create SSP2 document with dimensioned parameters and verify round-trip."""
    path = tmp_path / "dimensions.ssv"

    with SSV(path, "w", version="2.0") as ssv:
        param = ssv.xml.add_parameter(parname="matrix", ptype="Real", value="1.0 2.0 3.0 4.0")
        param.dimensions.append(Ssp2Dimension(size=2))
        param.dimensions.append(Ssp2Dimension(size=2))

    # Verify serialized XML has dimensions
    xml_text = path.read_text(encoding="utf-8")
    assert 'version="2.0"' in xml_text
    assert "Dimension" in xml_text

    # Read back and verify
    with SSV(path) as ssv:
        assert ssv.xml.version == "2.0"
        assert len(ssv.xml.parameters) == 1
        assert len(ssv.xml.parameters[0].dimensions) == 2
        assert ssv.xml.parameters[0].dimensions[0].size == 2
        assert ssv.xml.parameters[0].dimensions[1].size == 2


def test_float32_preserved_round_trip(ssv2_fixture: Path, tmp_path: Path):
    """T1: Float32 type preservation — load, verify type/value, round-trip, re-verify."""
    path = tmp_path / "float32_roundtrip.ssv"

    with SSV(ssv2_fixture) as ssv:
        param = ssv.xml.parameters[1]
        assert param.name == "example2"
        assert param.type_name == "Float32"
        assert param.attributes["value"] == "0.0 0.1 0.2 0.3 0.4 0.5 0.6"

        with SSV(path, "w", version="2.0") as wsv:
            wsv.xml.parameters.append(param)

    with SSV(path) as reloaded:
        p = reloaded.xml.parameters[0]
        assert p.type_name == "Float32"
        assert p.attributes["value"] == "0.0 0.1 0.2 0.3 0.4 0.5 0.6"


def test_uint32_preserved_round_trip(ssv2_fixture: Path, tmp_path: Path):
    """T2: UInt32 type preservation — load, verify type/value, round-trip, re-verify."""
    path = tmp_path / "uint32_roundtrip.ssv"

    with SSV(ssv2_fixture) as ssv:
        param = ssv.xml.parameters[2]
        assert param.name == "example3"
        assert param.type_name == "UInt32"
        assert param.attributes["value"] == "128"

        with SSV(path, "w", version="2.0") as wsv:
            wsv.xml.parameters.append(param)

    with SSV(path) as reloaded:
        p = reloaded.xml.parameters[0]
        assert p.type_name == "UInt32"
        assert p.attributes["value"] == "128"


def test_compliance_check_ssp2_fixture(ssv2_fixture: Path):
    """T3: Compliance check succeeds on SSP2 fixture."""
    with SSV(ssv2_fixture) as ssv:
        result = ssv.check_compliance()
        assert result is True


def test_edit_workflow_ssp2(ssv2_fixture: Path, tmp_path: Path):
    """T4: Load SSP2 fixture, add a parameter, save, reload, verify new parameter present."""
    path = tmp_path / "edited.ssv"

    with SSV(ssv2_fixture) as ssv:
        new_param = ssv.xml.add_parameter(parname="added_param", ptype="Real", value=42.0)
        # Save to new path by writing contents out
        with SSV(path, "w", version="2.0") as wsv:
            wsv.xml.parameters.extend(ssv.xml.parameters)
            wsv.xml.metadata = ssv.xml.metadata
            wsv.xml.name = ssv.xml.name

    with SSV(path) as reloaded:
        names = [p.name for p in reloaded.xml.parameters]
        assert "added_param" in names
        assert "example" in names
        assert "example2" in names
        assert "example3" in names
        assert len(reloaded.xml.parameters) == 4


def test_ssp2_version_mismatch_fails_gracefully(tmp_path: Path):
    """T5: Construct XML with SSP2 type element but version='1.0' — XSD validation raises."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ssv:ParameterSet
    xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues"
    version="1.0"
    name="BadVersion">
  <ssv:Parameters>
    <ssv:Parameter name="bad">
      <ssv:Float32 value="1.0"/>
    </ssv:Parameter>
  </ssv:Parameters>
</ssv:ParameterSet>"""
    path = tmp_path / "version_mismatch.ssv"
    path.write_text(xml_content, encoding="utf-8")

    with SSV(path) as ssv:
        # Loading succeeds (lax parse), but compliance validation must reject Float32 in SSP1
        with pytest.raises(ValueError, match="This element is not expected"):
            ssv.check_compliance()


@pytest.mark.parametrize("fixture_name", ["ssv2_fixture", "external_ssv_fixture"])
def test_round_trip_ssp1_and_ssp2(fixture_name: str, tmp_path: Path, request: pytest.FixtureRequest):
    """T6: Parameterized round-trip for both SSP1 and SSP2 SSV documents."""
    fixture_path: Path = request.getfixturevalue(fixture_name)
    out_path = tmp_path / f"roundtrip_{fixture_name}.ssv"

    with SSV(fixture_path) as ssv:
        original_version = ssv.xml.version
        original_count = len(ssv.xml.parameters)

        # Determine write version from the loaded document
        write_version = ssv.xml.version

        with SSV(out_path, "w", version=write_version) as wsv:
            wsv.xml.parameters.extend(ssv.xml.parameters)
            wsv.xml.name = ssv.xml.name

    with SSV(out_path) as reloaded:
        assert reloaded.xml.version == original_version
        assert len(reloaded.xml.parameters) == original_count