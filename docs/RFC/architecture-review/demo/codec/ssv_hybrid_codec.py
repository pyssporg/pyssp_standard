from ..generated.ssv2_generated_types import (
    ParameterSet as GeneratedParameterSet,
    Tparameter,
    Tparameters,
)
from ..model.ssv_model import Parameter, ParameterSet
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig


NS_SSV = "http://ssp-standard.org/SSP1/SystemStructureParameterValues"
NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"


class Ssv2HybridCodec:
    """Hybrid path: generated-style XML types + handwritten domain mapping."""

    def parse(self, xml_text: str) -> ParameterSet:
        normalized = xml_text.replace(NS_SSD, NS_SSV)
        generated = XmlParser().from_string(normalized, GeneratedParameterSet)

        parameters = []
        for p in generated.parameters.parameter:
            if p.real is None:
                continue
            if not p.real.value:
                continue
            parameters.append(
                Parameter(
                    name=p.name,
                    type_name="Real",
                    value=str(p.real.value[0]),
                )
            )

        return ParameterSet(
            name=generated.name,
            version=generated.version,
            parameters=parameters,
        )

    def serialize(self, model: ParameterSet, *, namespace_uri: str) -> str:
        generated = GeneratedParameterSet(
            name=model.name,
            version=model.version,
            parameters=Tparameters(
                parameter=[
                    Tparameter(
                        name=p.name,
                        real=Tparameter.Real(value=[float(p.value)]),
                    )
                    for p in model.parameters
                ]
            ),
        )
        xml = XmlSerializer(config=SerializerConfig(pretty_print=True)).render(
            generated,
            ns_map={
                "ssv": NS_SSV,
            },
        )

        if namespace_uri != NS_SSV:
            xml = xml.replace(
                NS_SSV,
                namespace_uri,
            )
        return xml
