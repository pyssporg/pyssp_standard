from __future__ import annotations

from pathlib import Path

from lxml import etree


SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schema"


def resolve_schema_path(*parts: str) -> Path:
    schema_path = SCHEMA_ROOT.joinpath(*parts)
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema does not exist: {schema_path}")
    return schema_path


class XmlSchemaValidator:
    """Shared XSD-backed XML validator."""

    def __init__(self, schema_path: Path, *, error_prefix: str):
        self.schema_path = schema_path
        self.error_prefix = error_prefix
        self._schema = etree.XMLSchema(etree.parse(str(self.schema_path)))

    def validate_xml(self, xml_text: str) -> None:
        document = etree.fromstring(xml_text.encode("utf-8"))
        if self._schema.validate(document):
            return

        error = self._schema.error_log.last_error
        if error is None:
            raise ValueError(self.error_prefix)
        raise ValueError(f"{self.error_prefix}: {error.message}")
