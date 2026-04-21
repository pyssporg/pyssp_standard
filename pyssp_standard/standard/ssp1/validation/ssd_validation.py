from __future__ import annotations

from pathlib import Path

from lxml import etree

from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1SystemStructureDescription


class Ssp1SsdSchemaValidator:
    def __init__(self, schema_path: Path | None = None):
        if schema_path is None:
            schema_path = (
                Path(__file__).resolve().parents[4]
                / "3rdParty"
                / "SSP1"
                / "schema"
                / "SystemStructureDescription.xsd"
            )
        self.schema_path = schema_path
        self._schema = etree.XMLSchema(etree.parse(str(self.schema_path)))

    def validate_xml(self, xml_text: str) -> None:
        document = etree.fromstring(xml_text.encode("utf-8"))
        if self._schema.validate(document):
            return
        error = self._schema.error_log.last_error
        if error is None:
            raise ValueError("SSD XML failed XSD validation")
        raise ValueError(f"SSD XML failed XSD validation: {error.message}")


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
