from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.fmi2.model.model_description import Fmi2ModelDescriptionDocument


DEFAULT_FMI2_MODEL_DESCRIPTION_SCHEMA_PATH = resolve_schema_path("FMI2", "fmi2ModelDescription.xsd")


class Fmi2ModelDescriptionSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_FMI2_MODEL_DESCRIPTION_SCHEMA_PATH,
            error_prefix="FMI2 modelDescription XML failed XSD validation",
        )


class Fmi2ModelDescriptionSemanticValidator:
    def validate(self, model: Fmi2ModelDescriptionDocument) -> None:
        if model.fmi_version != "2.0":
            raise ValueError(f"Unsupported FMI version '{model.fmi_version}'")
        if model.interface_type is None:
            raise ValueError("FMI2 modelDescription must declare ModelExchange or CoSimulation")

        seen_names: set[str] = set()
        for variable in model.variables:
            if variable.name in seen_names:
                raise ValueError(f"Duplicate variable '{variable.name}'")
            seen_names.add(variable.name)

        for type_definition in model.type_definitions:
            if type_definition.type_name == "Enumeration" and not type_definition.enumeration_items:
                raise ValueError(f"Enumeration type '{type_definition.name}' must define at least one Item")


class Fmi2ModelDescriptionValidator:
    def __init__(
        self,
        *,
        schema_validator: Fmi2ModelDescriptionSchemaValidator | None = None,
        semantic_validator: Fmi2ModelDescriptionSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Fmi2ModelDescriptionSchemaValidator()
        self.semantic_validator = semantic_validator or Fmi2ModelDescriptionSemanticValidator()

    def validate(self, model: Fmi2ModelDescriptionDocument, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
