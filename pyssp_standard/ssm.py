from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.codec.ssm_codec import Ssp1SsmCodec
from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1Transformation
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping
from pyssp_standard.standard.ssp1.validation import Ssp1SsmValidator
from pyssp_standard.common.xml_document import XmlDocument


class SSM(XmlDocument[Ssp1ParameterMapping]):
    """Public SSM facade following the same layered pattern as SSV."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsmCodec()
        self._validator = Ssp1SsmValidator()

    def _create_document(self) -> Ssp1ParameterMapping:
        return Ssp1ParameterMapping(version="1.0")

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
        if transformation is not None and not isinstance(transformation, Ssp1Transformation):
            transformation = Ssp1Transformation(
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
        if transformation is not None and not isinstance(transformation, Ssp1Transformation):
            kwargs["transformation"] = Ssp1Transformation(
                type_name=transformation.type_name,
                attributes={key: str(value) for key, value in transformation.attributes.items()},
            )
        return self.document.edit_mapping(**kwargs)
