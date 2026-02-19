from .ssv_codec_mapper import to_domain, to_generated
from .generated.ssv2_generated_types import GeneratedSsv2Codec
from .ssv_model import ParameterSet


class Ssv2HybridCodec:
    """Hybrid codec: generated XML types + handwritten domain mapping."""

    def parse(self, xml_text: str) -> ParameterSet:
        generated = GeneratedSsv2Codec.parse(xml_text)
        return to_domain(generated)

    def serialize(self, domain_model: ParameterSet) -> str:
        generated = to_generated(domain_model)
        return GeneratedSsv2Codec.serialize(generated)
