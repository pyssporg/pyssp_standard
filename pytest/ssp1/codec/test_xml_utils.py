from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.codec.xml_utils import (
    NS_SSC,
    NS_SSD,
    append_annotations,
    append_transformation,
    apply_metadata_attributes,
    find_type_child,
    parse_annotations_container,
    parse_enumerations_container,
    parse_metadata_attributes,
    parse_transformation,
    parse_units_container,
    qname,
    serialize_binding_prefix,
)
from pyssp_standard.standard.ssp1.model.ssc_model import (
    Ssp1Annotation,
    Ssp1BaseUnit,
    Ssp1DocumentMetadata,
    Ssp1Enumeration,
    Ssp1EnumerationItem,
    Ssp1Transformation,
    Ssp1Unit,
)


def test_base_unit_from_dict_normalizes_schema_attribute_names():
    unit = Ssp1BaseUnit.from_dict({"kg": 1, "A": -2, "K": 3, "factor": 2.5})

    assert unit.kg == 1
    assert unit.a == -2
    assert unit.k == 3
    assert unit.factor == 2.5


def test_document_metadata_round_trip_preserves_common_fields():
    root = ET.Element(qname(NS_SSD, "SystemStructureDescription"))
    metadata = Ssp1DocumentMetadata(
        id="meta-id",
        description="demo",
        author="tester",
        fileversion="1.2",
        copyright="copyright",
        license="MIT",
        generation_tool="tool",
        generation_date_and_time="2026-04-22T09:15:00Z",
    )

    apply_metadata_attributes(root, metadata)
    reparsed = parse_metadata_attributes(root)

    assert reparsed == metadata


def test_annotations_round_trip_preserves_type_and_xml_payload():
    root = ET.Element(qname(NS_SSD, "System"))
    annotation = Ssp1Annotation(
        type_name="com.example.note",
        elements=[ET.fromstring('<note xmlns="urn:test" level="info">hello</note>')],
    )

    append_annotations(root, [annotation], NS_SSD)
    reparsed = parse_annotations_container(root.find(qname(NS_SSD, "Annotations")))

    assert reparsed[0].type_name == "com.example.note"
    assert reparsed[0].elements[0].tag == "{urn:test}note"
    assert reparsed[0].elements[0].attrib == {"level": "info"}
    assert reparsed[0].elements[0].text == "hello"


def test_unit_round_trip_preserves_common_content_fields():
    root = ET.Element(qname(NS_SSD, "SystemStructureDescription"))
    unit = Ssp1Unit(
        name="km",
        id="u1",
        description="distance",
        base_unit=Ssp1BaseUnit(m=1, factor=1000.0),
    )

    from pyssp_standard.standard.ssp1.codec.xml_utils import append_units

    append_units(root, [unit], NS_SSD)
    reparsed = parse_units_container(root.find(qname(NS_SSD, "Units")))

    assert reparsed == [
        Ssp1Unit(
            name="km",
            id="u1",
            description="distance",
            base_unit=Ssp1BaseUnit(
                kg=None,
                m=1,
                s=None,
                a=None,
                k=None,
                mol=None,
                cd=None,
                rad=None,
                factor=1000.0,
                offset=None,
            ),
        )
    ]


def test_parse_units_container_reads_raw_ssp_unit_xml_with_schema_attribute_names():
    units_element = ET.fromstring(
        f"""\
<ssd:Units xmlns:ssc="{NS_SSC}" xmlns:ssd="{NS_SSD}">
  <ssc:Unit name="V">
    <ssc:BaseUnit kg="1" m="2" s="-3" A="-1" />
  </ssc:Unit>
</ssd:Units>
"""
    )

    reparsed = parse_units_container(units_element)

    assert len(reparsed) == 1
    unit = reparsed[0]
    assert unit.name == "V"
    assert unit.base_unit.kg == 1
    assert unit.base_unit.m == 2
    assert unit.base_unit.s == -3
    assert unit.base_unit.a == -1


def test_enumeration_round_trip_preserves_items_and_annotations():
    root = ET.Element(qname(NS_SSD, "SystemStructureDescription"))
    enumeration = Ssp1Enumeration(
        name="Gear",
        items=[Ssp1EnumerationItem(name="LOW", value=1), Ssp1EnumerationItem(name="HIGH", value=2)],
        annotations=[Ssp1Annotation(type_name="com.example.enum", elements=[ET.fromstring('<x xmlns="urn:test"/>')])],
    )

    from pyssp_standard.standard.ssp1.codec.xml_utils import append_enumerations

    append_enumerations(root, [enumeration], NS_SSD)
    reparsed = parse_enumerations_container(root.find(qname(NS_SSD, "Enumerations")))

    assert [(item.name, item.value) for item in reparsed[0].items] == [("LOW", 1), ("HIGH", 2)]
    assert reparsed[0].annotations[0].type_name == "com.example.enum"


def test_find_type_child_and_transformation_round_trip_preserve_shared_blocks():
    parent = ET.Element(qname(NS_SSD, "Connection"))
    ET.SubElement(parent, qname(NS_SSC, "LinearTransformation"), {"factor": "2", "offset": "0.5"})
    ET.SubElement(parent, qname(NS_SSD, "Annotations"))

    type_child = find_type_child(parent, exclude_local_names={"Annotations"})
    reparsed = parse_transformation(type_child)

    assert reparsed == Ssp1Transformation(type_name="LinearTransformation", attributes={"factor": "2", "offset": "0.5"})

    out_parent = ET.Element(qname(NS_SSD, "Connection"))
    append_transformation(
        out_parent,
        Ssp1Transformation(type_name="LinearTransformation", attributes={"factor": "2", "offset": "0.5"}),
    )
    assert out_parent[0].tag == qname(NS_SSC, "LinearTransformation")
    assert out_parent[0].attrib == {"factor": "2", "offset": "0.5"}


def test_binding_prefix_serialization_keeps_ssp_dot_convention():
    assert serialize_binding_prefix(None) is None
    assert serialize_binding_prefix("Plant") == "Plant."
    assert serialize_binding_prefix("Plant.") == "Plant."
