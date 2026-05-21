from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from pyssp_standard.srmd import ClassificationEntry, SRMD
from pyssp_standard.standard.ssp1.codec.srmd_codec import NS_SRMD, NS_STC, NS_XLINK
from pyssp_standard.standard.ssp1.model import Ssp1Annotation


def test_check_compliance_accepts_reference_fixture():
    with SRMD("pytest/__fixture__/test_schema_validation.srmd") as srmd:
        assert srmd.check_compliance() is True
        assert len(srmd.xml.classifications) == 1


def test_create_and_read_round_trip(tmp_path):
    path = tmp_path / "test.srmd"

    with SRMD(path, "w") as srmd:
        srmd.xml.metadata.description = "Test resource"
        srmd.xml.metadata.annotations.append(
            Ssp1Annotation(
                type_name="com.example.doc",
                elements=[ET.fromstring('<doc xmlns="urn:test">meta</doc>')],
            )
        )
        srmd.xml.data = "resources/stimuli.csv"
        srmd.xml.checksum = "DEADBEEF"
        srmd.xml.checksum_type = "SHA3-256"

        classification = srmd.xml.add_classification("com.example.info", href="types/info.md", linked_type="text/markdown")
        classification.entries.append(
            ClassificationEntry(
                keyword="plain",
                text="value",
                description="entry",
            )
        )
        classification.add_entry(
            "xml",
            type="application/xml",
            content=[ET.fromstring('<node xmlns="urn:test" mode="full"><child /></node>')],
        )
        assert srmd.check_compliance() is True

    with SRMD(path) as srmd:
        assert srmd.xml.metadata.description == "Test resource"
        assert srmd.xml.metadata.annotations[0].elements[0].text == "meta"
        assert srmd.xml.data == "resources/stimuli.csv"
        assert srmd.xml.checksum == "DEADBEEF"
        assert srmd.xml.classifications[0].href == "types/info.md"
        assert srmd.xml.classifications[0].linked_type == "text/markdown"
        assert srmd.xml.classifications[0].entries[0].text == "value"
        assert srmd.xml.classifications[0].entries[1].content[0].attrib == {"mode": "full"}


def test_serialized_xml_uses_traceability_namespaces(tmp_path):
    path = tmp_path / "namespaces.srmd"

    with SRMD(path, "w") as srmd:
        classification = srmd.xml.add_classification("com.example.doc", href="docs/spec.md")
        classification.add_entry("ref", href="docs/entry.md", linked_type="text/markdown")

    root = ET.parse(path).getroot()
    assert root.tag == f"{{{NS_SRMD}}}SimulationResourceMetaData"
    classification = next(child for child in root if child.tag == f"{{{NS_STC}}}Classification")
    assert classification.attrib[f"{{{NS_XLINK}}}href"] == "docs/spec.md"
    entry = next(child for child in classification if child.tag == f"{{{NS_STC}}}ClassificationEntry")
    assert entry.attrib[f"{{{NS_XLINK}}}href"] == "docs/entry.md"


def test_duplicate_classification_types_fail_semantic_validation(tmp_path):
    path = tmp_path / "duplicate.srmd"

    with pytest.raises(ValueError, match="Duplicate classification type"):
        with SRMD(path, "w") as srmd:
            srmd.xml.add_classification("com.example.duplicate")
            srmd.xml.add_classification("com.example.duplicate")
            srmd.check_compliance()
