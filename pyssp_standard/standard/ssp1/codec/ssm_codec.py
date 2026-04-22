from __future__ import annotations

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from pyssp_standard.standard.ssp1.codec.ssm_xsdata_mapper import Ssp1SsmXsdataMapper
from pyssp_standard.standard.ssp1.generated.ssm_generated_types import ParameterMapping
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping, Ssp1MappingEntry, Ssp1Transformation


NS_SSM = "http://ssp-standard.org/SSP1/SystemStructureParameterMapping"
NS_SSC = "http://ssp-standard.org/SSP1/SystemStructureCommon"


class Ssp1SsmCodec:
    """SSP1 SSM codec backed by xsdata-generated bindings."""

    def __init__(self):
        self._parser = XmlParser()
        self._serializer = XmlSerializer(config=SerializerConfig(indent="  "))
        self._mapper = Ssp1SsmXsdataMapper()

    def parse(self, xml_text: str) -> Ssp1ParameterMapping:
        generated = self._parser.from_string(xml_text, ParameterMapping)
        return self._mapper.read_parameter_mapping(generated)

    def serialize(self, document: Ssp1ParameterMapping) -> str:
        generated = self._mapper.write_parameter_mapping(document)
        return self._serializer.render(generated, ns_map={"ssm": NS_SSM, "ssc": NS_SSC})
