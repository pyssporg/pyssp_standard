from __future__ import annotations

from pathlib import Path

from lxml import etree

from pyssp_standard.ssp1.model.ssv_model import SsvParameterSet


class Ssp1SsvSchemaValidator:
    def __init__(self, schema_path: Path | None = None):
        if schema_path is None:
            schema_path = (
                Path(__file__).resolve().parents[3]
                / "3rdParty"
                / "SSP1"
                / "schema"
                / "SystemStructureParameterValues.xsd"
            )
        self.schema_path = schema_path
        self._schema = etree.XMLSchema(etree.parse(str(self.schema_path)))

    def validate_xml(self, xml_text: str) -> None:
        document = etree.fromstring(xml_text.encode("utf-8"))
        if self._schema.validate(document):
            return

        error = self._schema.error_log.last_error
        if error is None:
            raise ValueError("SSV XML failed XSD validation")
        raise ValueError(f"SSV XML failed XSD validation: {error.message}")


class Ssp1SsvSemanticValidator:
    def validate(self, model: SsvParameterSet) -> None:
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

    def validate(self, model: SsvParameterSet, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
