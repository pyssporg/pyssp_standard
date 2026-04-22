from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping


DEFAULT_SSP1_SSM_SCHEMA_PATH = resolve_schema_path("SSP1", "SystemStructureParameterMapping.xsd")


class Ssp1SsmSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_SSP1_SSM_SCHEMA_PATH,
            error_prefix="SSM XML failed XSD validation",
        )


class Ssp1SsmSemanticValidator:
    def validate(self, model: Ssp1ParameterMapping) -> None:
        seen_targets: set[str] = set()
        for mapping in model.mappings:
            if mapping.target in seen_targets:
                raise ValueError(f"Duplicate mapping target '{mapping.target}'")
            seen_targets.add(mapping.target)


class Ssp1SsmValidator:
    def __init__(
        self,
        *,
        schema_validator: Ssp1SsmSchemaValidator | None = None,
        semantic_validator: Ssp1SsmSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Ssp1SsmSchemaValidator()
        self.semantic_validator = semantic_validator or Ssp1SsmSemanticValidator()

    def validate(self, model: Ssp1ParameterMapping, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
