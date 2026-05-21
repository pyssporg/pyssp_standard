from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.fmi3.model.model_description import Fmi3ModelDescriptionDocument


DEFAULT_FMI3_MODEL_DESCRIPTION_SCHEMA_PATH = resolve_schema_path("FMI3", "fmi3ModelDescription.xsd")


class Fmi3ModelDescriptionSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_FMI3_MODEL_DESCRIPTION_SCHEMA_PATH,
            error_prefix="FMI3 modelDescription XML failed XSD validation",
        )


class Fmi3ModelDescriptionSemanticValidator:
    def validate(self, model: Fmi3ModelDescriptionDocument) -> None:
        if not model.fmi_version.startswith("3."):
            raise ValueError(f"Unsupported FMI version '{model.fmi_version}'")
        if not model.instantiation_token:
            raise ValueError("FMI3 modelDescription must provide an instantiationToken")

        seen_names: set[str] = set()
        for variable in model.variables:
            if variable.name in seen_names:
                raise ValueError(f"Duplicate variable '{variable.name}'")
            seen_names.add(variable.name)

        for type_definition in model.type_definitions:
            if type_definition.type_name == "Enumeration" and not type_definition.enumeration_items:
                raise ValueError(f"Enumeration type '{type_definition.name}' must define at least one Item")


class Fmi3ModelDescriptionValidator:
    def __init__(
        self,
        *,
        schema_validator: Fmi3ModelDescriptionSchemaValidator | None = None,
        semantic_validator: Fmi3ModelDescriptionSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Fmi3ModelDescriptionSchemaValidator()
        self.semantic_validator = semantic_validator or Fmi3ModelDescriptionSemanticValidator()

    def validate(self, model: Fmi3ModelDescriptionDocument, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)