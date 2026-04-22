from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet


DEFAULT_SSP1_SSV_SCHEMA_PATH = resolve_schema_path("SSP1", "SystemStructureParameterValues.xsd")


class Ssp1SsvSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_SSP1_SSV_SCHEMA_PATH,
            error_prefix="SSV XML failed XSD validation",
        )


class Ssp1SsvSemanticValidator:
    def validate(self, model: Ssp1ParameterSet) -> None:
        seen_parameter_names: set[str] = set()
        for parameter in model.parameters:
            if parameter.name in seen_parameter_names:
                raise ValueError(f"Duplicate parameter '{parameter.name}'")
            seen_parameter_names.add(parameter.name)

        seen_units: set[str] = set()
        for unit in model.units:
            if unit.name in seen_units:
                raise ValueError(f"Duplicate unit '{unit.name}'")
            seen_units.add(unit.name)

        for parameter in model.parameters:
            unit_name = parameter.attributes.get("unit")
            if unit_name is not None and not self._is_known_unit(unit_name, seen_units):
                raise ValueError(f"Parameter '{parameter.name}' references unknown unit '{unit_name}'")

    @staticmethod
    def _is_known_unit(unit_name: str, declared_units: set[str]) -> bool:
        if unit_name in declared_units:
            return True
        if unit_name.startswith("[") and unit_name.endswith("]") and len(unit_name) > 2:
            return True
        return False


class Ssp1SsvValidator:
    def __init__(
        self,
        *,
        schema_validator: Ssp1SsvSchemaValidator | None = None,
        semantic_validator: Ssp1SsvSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Ssp1SsvSchemaValidator()
        self.semantic_validator = semantic_validator or Ssp1SsvSemanticValidator()

    def validate(self, model: Ssp1ParameterSet, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
