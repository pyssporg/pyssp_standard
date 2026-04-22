from __future__ import annotations

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from pyssp_standard.standard.ssp1.codec.ssd_xsdata_mapper import Ssp1SsdXsdataMapper
from pyssp_standard.standard.ssp1.generated.ssd_generated_types import SystemStructureDescription
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1SystemStructureDescription


NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"
NS_SSC = "http://ssp-standard.org/SSP1/SystemStructureCommon"
NS_SSM = "http://ssp-standard.org/SSP1/SystemStructureParameterMapping"
NS_SSV = "http://ssp-standard.org/SSP1/SystemStructureParameterValues"


class Ssp1SsdCodec:
    """SSP1 SSD codec backed by xsdata-generated bindings."""

    def __init__(self):
        self._parser = XmlParser()
        self._serializer = XmlSerializer(config=SerializerConfig(indent="  "))
        self._mapper = Ssp1SsdXsdataMapper()

    def parse(self, xml_text: str) -> Ssd1SystemStructureDescription:
        generated = self._parser.from_string(xml_text, SystemStructureDescription)
        return self._mapper.read_system_structure_description(generated)

    def serialize(self, document: Ssd1SystemStructureDescription) -> str:
        generated = self._mapper.write_system_structure_description(document)
        return self._serializer.render(
            generated,
            ns_map={"ssd": NS_SSD, "ssc": NS_SSC, "ssm": NS_SSM, "ssv": NS_SSV},
        )
