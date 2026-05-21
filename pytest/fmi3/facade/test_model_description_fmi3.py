"""ModelDescription facade tests for FMI3 (version 3.0) documents."""

from __future__ import annotations

from pathlib import Path

from pyssp_standard.md import ModelDescription


def test_create_fmi3_document_round_trip(tmp_path: Path):
    """Create FMI3 document, write, read back, verify version."""
    path = tmp_path / "test_fmi3.xml"

    with ModelDescription(path, "w", version="3.0") as md:
        assert md.xml.fmi_version == "3.0"

    xml_text = path.read_text(encoding="utf-8")
    assert 'fmiVersion="3.0"' in xml_text

    with ModelDescription(path) as md:
        assert md.xml.fmi_version == "3.0"