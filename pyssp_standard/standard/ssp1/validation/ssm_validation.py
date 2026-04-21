from __future__ import annotations

from pathlib import Path

from lxml import etree

from pyssp_standard.standard.ssp1.model.ssm_model import SsmParameterMapping


class Ssp1SsmSchemaValidator:
    def __init__(self, schema_path: Path | None = None):
        if schema_path is None:
            schema_path = (
                Path(__file__).resolve().parents[4]
                / "3rdParty"
                / "SSP1"
                / "schema"
                / "SystemStructureParameterMapping.xsd"
            )
        self.schema_path = schema_path
        self._schema = etree.XMLSchema(etree.parse(str(self.schema_path)))

    def validate_xml(self, xml_text: str) -> None:
        document = etree.fromstring(xml_text.encode("utf-8"))
        if self._schema.validate(document):
            return
        error = self._schema.error_log.last_error
        if error is None:
            raise ValueError("SSM XML failed XSD validation")
        raise ValueError(f"SSM XML failed XSD validation: {error.message}")


class Ssp1SsmSemanticValidator:
    def validate(self, model: SsmParameterMapping) -> None:
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

    def validate(self, model: SsmParameterMapping, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
