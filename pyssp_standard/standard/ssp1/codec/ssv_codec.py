from __future__ import annotations

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from pyssp_standard.standard.ssp1.codec.ssv_xsdata_mapper import Ssp1SsvXsdataMapper
from pyssp_standard.standard.ssp1.generated.ssv_generated_types import ParameterSet
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet


NS_SSV = "http://ssp-standard.org/SSP1/SystemStructureParameterValues"




class Ssp1SsvXsdataCodec:
    def __init__(self):
        self._parser = XmlParser()
        self._serializer = XmlSerializer(config=SerializerConfig(indent="  "))
        self._mapper = Ssp1SsvXsdataMapper()

    def parse(self, xml_text: str) -> Ssp1ParameterSet:
        generated = self._parser.from_string(xml_text, ParameterSet)
        return self._mapper.read_parameterset(generated)

    def serialize(self, model: Ssp1ParameterSet) -> str:
        generated = self._mapper.write_parameterset(model)
        return self._serializer.render(generated, ns_map={"ssv": NS_SSV})
