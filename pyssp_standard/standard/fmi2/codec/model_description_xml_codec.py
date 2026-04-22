from __future__ import annotations

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from pyssp_standard.standard.fmi2.codec.model_description_xsdata_mapper import Fmi2ModelDescriptionXsdataMapper
from pyssp_standard.standard.fmi2.generated.model_description_generated_types import FmiModelDescription
from pyssp_standard.standard.fmi2.model.model_description import Fmi2ModelDescriptionDocument


class Fmi2ModelDescriptionXmlCodec:
    """FMI2 modelDescription codec backed by xsdata-generated bindings."""

    def __init__(self):
        self._parser = XmlParser()
        self._serializer = XmlSerializer(config=SerializerConfig(indent="  "))
        self._mapper = Fmi2ModelDescriptionXsdataMapper()

    def parse(self, xml_text: str) -> Fmi2ModelDescriptionDocument:
        generated = self._parser.from_string(xml_text, FmiModelDescription)
        return self._mapper.read_model_description(generated)

    def serialize(self, document: Fmi2ModelDescriptionDocument) -> str:
        generated = self._mapper.write_model_description(document)
        return self._serializer.render(generated)
