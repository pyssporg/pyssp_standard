from .generated.ssv2_generated_types import (
    GeneratedSsv2Codec,
    GeneratedSsv2Parameter,
    GeneratedSsv2ParameterSet,
    GeneratedSsv2Value,
)
from .parameter_model import Parameter, ParameterSet


class Ssv2HybridCodec:
    """Hybrid path: generated-style XML types + handwritten domain mapping."""

    def parse(self, xml_text: str) -> ParameterSet:
        generated = GeneratedSsv2Codec.parse(xml_text)
        return ParameterSet(
            name=generated.name,
            version=generated.version,
            parameters=[
                Parameter(name=p.name, type_name=p.value.type_name, value=p.value.value)
                for p in generated.parameters
            ],
        )

    def serialize(self, model: ParameterSet, *, namespace_uri: str) -> str:
        generated = GeneratedSsv2ParameterSet(
            name=model.name,
            version=model.version,
            parameters=[
                GeneratedSsv2Parameter(
                    name=p.name,
                    value=GeneratedSsv2Value(type_name=p.type_name, value=p.value),
                )
                for p in model.parameters
            ],
        )
        xml = GeneratedSsv2Codec.serialize(generated)

        if namespace_uri != "http://ssp-standard.org/SSP1/SystemStructureParameterValues":
            xml = xml.replace(
                "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
                namespace_uri,
            )
        return xml
