from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from pyssp_standard.common.xml_schema_validation import resolve_schema_path
from pyssp_standard.standard.ssp1.codec.srmd_codec import NS_SRMD, NS_STC
from pyssp_standard.standard.ssp1.codec.xml_utils import qname
from pyssp_standard.standard.ssp1.model.srmd_model import Ssp1SimulationResourceMetaData


DEFAULT_SSP1_SRMD_SCHEMA_PATH = resolve_schema_path("SSP-LS-Traceability", "SRMD.xsd")


class Ssp1SrmdSchemaValidator:
    def __init__(self, schema_path: Path | None = None):
        self.schema_path = schema_path or DEFAULT_SSP1_SRMD_SCHEMA_PATH

    def validate_xml(self, xml_text: str) -> None:
        root = ET.fromstring(xml_text)

        if root.tag != qname(NS_SRMD, "SimulationResourceMetaData"):
            raise ValueError("SRMD XML failed structural validation: root element must be srmd:SimulationResourceMetaData")
        if "version" not in root.attrib:
            raise ValueError("SRMD XML failed structural validation: missing required attribute 'version'")
        if "name" not in root.attrib:
            raise ValueError("SRMD XML failed structural validation: missing required attribute 'name'")

        for child in root:
            if child.tag == qname(NS_STC, "Classification"):
                self._validate_classification(child)
                continue
            if child.tag == qname(NS_STC, "Annotations"):
                continue
            raise ValueError(
                "SRMD XML failed structural validation: unsupported child "
                f"'{child.tag}' under srmd:SimulationResourceMetaData"
            )

    def _validate_classification(self, element: ET.Element) -> None:
        for child in element:
            if child.tag != qname(NS_STC, "ClassificationEntry"):
                raise ValueError(
                    "SRMD XML failed structural validation: unsupported child "
                    f"'{child.tag}' under stc:Classification"
                )
            if "keyword" not in child.attrib:
                raise ValueError(
                    "SRMD XML failed structural validation: missing required attribute "
                    "'keyword' on stc:ClassificationEntry"
                )


class Ssp1SrmdSemanticValidator:
    def validate(self, model: Ssp1SimulationResourceMetaData) -> None:
        seen_types: set[str] = set()
        for classification in model.classifications:
            if classification.type is None:
                continue
            if classification.type in seen_types:
                raise ValueError(f"Duplicate classification type '{classification.type}'")
            seen_types.add(classification.type)


class Ssp1SrmdValidator:
    def __init__(
        self,
        *,
        schema_validator: Ssp1SrmdSchemaValidator | None = None,
        semantic_validator: Ssp1SrmdSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Ssp1SrmdSchemaValidator()
        self.semantic_validator = semantic_validator or Ssp1SrmdSemanticValidator()

    def validate(self, model: Ssp1SimulationResourceMetaData, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
