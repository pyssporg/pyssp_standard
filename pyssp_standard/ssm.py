from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.codec.ssm_xml_codec import Ssp1SsmXmlCodec
from pyssp_standard.standard.ssp1.model.ssm_model import SsmParameterMapping, SsmTransformation
from pyssp_standard.standard.ssp1.validation import Ssp1SsmValidator
from pyssp_standard.xml_document import XmlDocumentFacade


class SSM(XmlDocumentFacade[SsmParameterMapping]):
    """Public SSM facade following the same layered pattern as SSV."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsmXmlCodec()
        self._validator = Ssp1SsmValidator()

    def _create_document(self) -> SsmParameterMapping:
        return SsmParameterMapping(version="1.0")

    @property
    def version(self) -> str:
        return self.document.version

    @version.setter
    def version(self, value: str) -> None:
        self.document.version = value

    @property
    def mappings(self):
        return self.document.mappings

    def add_mapping(self, source: str, target: str, *, suppress_unit_conversion=None, transformation=None):
        if transformation is not None and not isinstance(transformation, SsmTransformation):
            transformation = SsmTransformation(
                type_name=transformation.type_name,
                attributes={key: str(value) for key, value in transformation.attributes.items()},
            )
        return self.document.add_mapping(
            source,
            target,
            suppress_unit_conversion=suppress_unit_conversion,
            transformation=transformation,
        )

    def edit_mapping(self, **kwargs):
        transformation = kwargs.get("transformation")
        if transformation is not None and not isinstance(transformation, SsmTransformation):
            kwargs["transformation"] = SsmTransformation(
                type_name=transformation.type_name,
                attributes={key: str(value) for key, value in transformation.attributes.items()},
            )
        return self.document.edit_mapping(**kwargs)
