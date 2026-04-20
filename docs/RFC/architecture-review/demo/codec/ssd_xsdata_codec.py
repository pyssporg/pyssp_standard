from __future__ import annotations

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from ..model.ssd_model import SsdDocument
from .ssd_mapper import NS_SSD, SsdXsdataMapper


class SsdXsdataCodec:
    """SSD codec example using xsdata-generated bindings plus a handwritten mapper.

    This is intentionally separate from the demo's current handwritten SSD codec.
    It shows the recommended split when SSD is moved to xsdata:
    - xsdata-generated types own the XML/schema shape
    - this codec owns parser/serializer orchestration only
    - SsdXsdataMapper owns generated <-> domain mapping
    """

    def __init__(self, ssv_codec):
        self._mapper = SsdXsdataMapper(ssv_codec=ssv_codec)
        self._parser = XmlParser()
        self._serializer = XmlSerializer(config=SerializerConfig(indent="  "))

    def parse(self, xml_text: str) -> SsdDocument:
        generated_root = self._generated_root_type()
        generated = self._parser.from_string(xml_text, generated_root)
        return self._mapper.to_domain(generated)

    def serialize(self, doc: SsdDocument) -> str:
        generated = self._mapper.from_domain(doc)
        return self._serializer.render(
            generated,
            ns_map={
                "ssd": NS_SSD,
            },
        )

    @staticmethod
    def _generated_root_type():
        try:
            from ..generated.ssd_generated_types import SystemStructureDescription
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "SSD xsdata bindings are not generated yet. Run "
                "`./venv/bin/python docs/RFC/architecture-review/demo/generated/generate_ssd_bindings.py` "
                "to create docs/RFC/architecture-review/demo/generated/ssd_generated_types.py."
            ) from exc

        return SystemStructureDescription
