from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1SystemStructureDescription


DEFAULT_SSP1_SSD_SCHEMA_PATH = resolve_schema_path("SSP1", "SystemStructureDescription.xsd")


class Ssp1SsdSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_SSP1_SSD_SCHEMA_PATH,
            error_prefix="SSD XML failed XSD validation",
        )


class Ssp1SsdSemanticValidator:
    def validate(self, model: Ssd1SystemStructureDescription) -> None:
        if model.system is None:
            raise ValueError("SSD document must contain a root system")

        component_names: set[str] = set()
        for component in model.system.elements:
            if component.name in component_names:
                raise ValueError(f"Duplicate component '{component.name}'")
            component_names.add(component.name)

        connector_names: set[str] = set()
        for connector in model.system.connectors:
            if connector.name in connector_names:
                raise ValueError(f"Duplicate system connector '{connector.name}'")
            connector_names.add(connector.name)


class Ssp1SsdValidator:
    def __init__(
        self,
        *,
        schema_validator: Ssp1SsdSchemaValidator | None = None,
        semantic_validator: Ssp1SsdSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Ssp1SsdSchemaValidator()
        self.semantic_validator = semantic_validator or Ssp1SsdSemanticValidator()

    def validate(self, model: Ssd1SystemStructureDescription, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
