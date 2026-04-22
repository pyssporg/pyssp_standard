from __future__ import annotations

import pytest
from xml.etree import ElementTree as ET

from pyssp_standard.ssb import SSB
from pyssp_standard.standard.ssp1.model import Ssp1Annotation, Ssp1EnumerationItem


def test_create_round_trip_preserves_entries_units_and_enumerations(tmp_path):
    path = tmp_path / "test.ssb"

    with SSB(path, "w") as ssb:
        ssb.xml.add_entry("speed", "Real", unit="m/s")
        ssb.xml.add_entry("state", "Enumeration", enumeration="Gear")
        ssb.xml.add_unit("m/s", {"m": 1, "s": -1})
        ssb.xml.add_enumeration(
            "Gear",
            [Ssp1EnumerationItem(name="LOW", value=1), Ssp1EnumerationItem(name="HIGH", value=2)],
        )
        assert ssb.check_compliance() is True

    with SSB(path) as ssb:
        assert len(ssb.xml.entries) == 2
        assert ssb.xml.entries[0].attributes == {"unit": "m/s"}
        assert ssb.xml.entries[1].attributes == {"name": "Gear"}
        assert ssb.xml.units[0].name == "m/s"
        assert ssb.xml.enumerations[0].name == "Gear"


def test_round_trip_preserves_entry_annotations(tmp_path):
    path = tmp_path / "annotations.ssb"

    with SSB(path, "w") as ssb:
        entry = ssb.xml.add_entry("payload", "Binary", mimetype="application/octet-stream")
        entry.annotations.append(
            Ssp1Annotation(
                type_name="com.example.entry",
                elements=[ET.fromstring('<hint xmlns="urn:test" mode="raw">payload</hint>')],
            )
        )

    with SSB(path) as ssb:
        assert ssb.xml.entries[0].annotations[0].type_name == "com.example.entry"
        assert ssb.xml.entries[0].annotations[0].elements[0].attrib == {"mode": "raw"}


def test_compliance_rejects_unknown_enumeration_reference(tmp_path):
    path = tmp_path / "invalid.ssb"

    with SSB(path, "w") as ssb:
        ssb.xml.add_entry("state", "Enumeration", enumeration="MissingEnum")

        with pytest.raises(ValueError, match="references unknown enumeration 'MissingEnum'"):
            ssb.check_compliance()
