from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.codec import Ssp1SrmdCodec


def test_parses_reference_fixture():
    fixture = Path("pytest/__fixture__/test_schema_validation.srmd")
    document = Ssp1SrmdCodec().parse(fixture.read_text(encoding="utf-8"))

    assert document.version == "1.0.0-beta2"
    assert document.name == "Stimuli Meta-Data"
    assert len(document.classifications) == 1
    assert document.classifications[0].type == "de.setlevel.srmd.ISO-11010-X"
    assert document.classifications[0].entries[0].keyword == "part"
