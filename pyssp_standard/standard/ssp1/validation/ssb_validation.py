from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.ssp1.model.ssb_model import Ssp1SignalDictionary


DEFAULT_SSP1_SSB_SCHEMA_PATH = resolve_schema_path("SSP1", "SystemStructureSignalDictionary.xsd")


class Ssp1SsbSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_SSP1_SSB_SCHEMA_PATH,
            error_prefix="SSB XML failed XSD validation",
        )


class Ssp1SsbSemanticValidator:
    def validate(self, model: Ssp1SignalDictionary) -> None:
        seen_entry_names: set[str] = set()
        for entry in model.entries:
            if entry.name in seen_entry_names:
                raise ValueError(f"Duplicate dictionary entry '{entry.name}'")
            seen_entry_names.add(entry.name)

        seen_units: set[str] = set()
        for unit in model.units:
            if unit.name in seen_units:
                raise ValueError(f"Duplicate unit '{unit.name}'")
            seen_units.add(unit.name)

        seen_enumerations: set[str] = set()
        for enumeration in model.enumerations:
            if enumeration.name in seen_enumerations:
                raise ValueError(f"Duplicate enumeration '{enumeration.name}'")
            seen_enumerations.add(enumeration.name)

        for entry in model.entries:
            unit_name = entry.attributes.get("unit")
            if unit_name is not None and not self._is_known_unit(unit_name, seen_units):
                raise ValueError(f"Dictionary entry '{entry.name}' references unknown unit '{unit_name}'")
            enumeration_name = entry.attributes.get("name") if entry.type_name == "Enumeration" else None
            if enumeration_name is not None and enumeration_name not in seen_enumerations:
                raise ValueError(
                    f"Dictionary entry '{entry.name}' references unknown enumeration '{enumeration_name}'"
                )

    @staticmethod
    def _is_known_unit(unit_name: str, declared_units: set[str]) -> bool:
        if unit_name in declared_units:
            return True
        if unit_name.startswith("[") and unit_name.endswith("]") and len(unit_name) > 2:
            return True
        return False


class Ssp1SsbValidator:
    def __init__(
        self,
        *,
        schema_validator: Ssp1SsbSchemaValidator | None = None,
        semantic_validator: Ssp1SsbSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Ssp1SsbSchemaValidator()
        self.semantic_validator = semantic_validator or Ssp1SsbSemanticValidator()

    def validate(self, model: Ssp1SignalDictionary, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
