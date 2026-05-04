from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.ls_ref.model.experiments import LSRefExperimentsDocument


DEFAULT_LS_REF_EXPERIMENTS_SCHEMA_PATH = resolve_schema_path(
    "FMI3",
    "fmi3LayeredStandardReferenceExperiments.xsd",
)


class LSRefExperimentsSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_LS_REF_EXPERIMENTS_SCHEMA_PATH,
            error_prefix="LS-REF experiments XML failed XSD validation",
        )


class LSRefExperimentsSemanticValidator:
    def validate(self, model: LSRefExperimentsDocument) -> None:
        seen_names: set[str] = set()
        for experiment in model.experiments:
            if experiment.name in seen_names:
                raise ValueError(f"Duplicate experiment name '{experiment.name}'")
            seen_names.add(experiment.name)


class LSRefExperimentsValidator:
    def __init__(
        self,
        *,
        schema_validator: LSRefExperimentsSchemaValidator | None = None,
        semantic_validator: LSRefExperimentsSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or LSRefExperimentsSchemaValidator()
        self.semantic_validator = semantic_validator or LSRefExperimentsSemanticValidator()

    def validate(self, model: LSRefExperimentsDocument, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
