from __future__ import annotations

from pyssp_standard.standard.ssp1.codec import Ssp1SsbCodec
from pyssp_standard.standard.ssp1.model import Ssp1Annotation, Ssp1EnumerationItem
from xml.etree import ElementTree as ET


def test_parses_signal_dictionary_xml():
    xml_text = """\
<ssb:SignalDictionary xmlns:ssb="http://ssp-standard.org/SSP1/SystemStructureSignalDictionary"
                      xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon"
                      version="1.0">
  <ssb:DictionaryEntry name="speed">
    <ssc:Real unit="m/s" />
  </ssb:DictionaryEntry>
  <ssb:Enumerations>
    <ssc:Enumeration name="Gear">
      <ssc:Item name="LOW" value="1" />
      <ssc:Item name="HIGH" value="2" />
    </ssc:Enumeration>
  </ssb:Enumerations>
</ssb:SignalDictionary>
"""
    document = Ssp1SsbCodec().parse(xml_text)

    assert document.version == "1.0"
    assert len(document.entries) == 1
    assert document.entries[0].name == "speed"
    assert document.entries[0].type_name == "Real"
    assert document.entries[0].attributes == {"unit": "m/s"}
    assert document.enumerations[0].name == "Gear"


def test_round_trip_preserves_units_enumerations_and_annotations():
    codec = Ssp1SsbCodec()
    document = codec.parse(
        """\
<ssb:SignalDictionary xmlns:ssb="http://ssp-standard.org/SSP1/SystemStructureSignalDictionary"
                      xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon"
                      version="1.0">
  <ssb:DictionaryEntry name="state">
    <ssc:Enumeration name="Gear" />
  </ssb:DictionaryEntry>
</ssb:SignalDictionary>
"""
    )
    document.add_unit("m/s", {"m": 1, "s": -1})
    document.add_enumeration(
        "Gear",
        [Ssp1EnumerationItem(name="LOW", value=1), Ssp1EnumerationItem(name="HIGH", value=2)],
    )
    document.entries[0].annotations.append(
        Ssp1Annotation(
            type_name="com.example.entry",
            elements=[ET.fromstring('<note xmlns="urn:test">ok</note>')],
        )
    )

    reparsed = codec.parse(codec.serialize(document))

    assert reparsed.entries[0].type_name == "Enumeration"
    assert reparsed.entries[0].attributes == {"name": "Gear"}
    assert reparsed.units[0].name == "m/s"
    assert [(item.name, item.value) for item in reparsed.enumerations[0].items] == [("LOW", 1), ("HIGH", 2)]
    assert reparsed.entries[0].annotations[0].elements[0].text == "ok"
