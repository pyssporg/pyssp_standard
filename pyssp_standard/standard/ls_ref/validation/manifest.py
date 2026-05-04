from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.ls_ref.model.manifest import LSRefManifestDocument


DEFAULT_LS_REF_MANIFEST_SCHEMA_PATH = resolve_schema_path(
    "FMI3",
    "fmi3LayeredStandardReferenceManifest.xsd",
)


class LSRefManifestSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_LS_REF_MANIFEST_SCHEMA_PATH,
            error_prefix="LS-REF manifest XML failed XSD validation",
        )


class LSRefManifestSemanticValidator:
    def validate(self, model: LSRefManifestDocument) -> None:
        seen_sources: set[str] = set()
        for related in model.related:
            if related.source in seen_sources:
                raise ValueError(f"Duplicate related source '{related.source}'")
            seen_sources.add(related.source)


class LSRefManifestValidator:
    def __init__(
        self,
        *,
        schema_validator: LSRefManifestSchemaValidator | None = None,
        semantic_validator: LSRefManifestSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or LSRefManifestSchemaValidator()
        self.semantic_validator = semantic_validator or LSRefManifestSemanticValidator()

    def validate(self, model: LSRefManifestDocument, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
