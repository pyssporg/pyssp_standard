from __future__ import annotations

from pyssp_standard.standard.ssp1.generated.ssm_generated_types import ParameterMapping, TmappingEntry
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1MappingEntry, Ssp1ParameterMapping, Ssp1Transformation


class Ssp1SsmXsdataMapper:
    def read_parameter_mapping(self, generated: ParameterMapping) -> Ssp1ParameterMapping:
        document = Ssp1ParameterMapping(version=generated.version)
        for entry in generated.mapping_entry:
            document.mappings.append(
                Ssp1MappingEntry(
                    source=entry.source,
                    target=entry.target,
                    suppress_unit_conversion=self._read_suppress_unit_conversion(entry),
                    transformation=self._read_transformation(entry),
                )
            )
        return document

    def write_parameter_mapping(self, model: Ssp1ParameterMapping) -> ParameterMapping:
        return ParameterMapping(
            version=model.version,
            mapping_entry=[self._write_mapping_entry(entry) for entry in model.mappings],
        )

    @staticmethod
    def _read_suppress_unit_conversion(entry: TmappingEntry) -> bool | None:
        return True if entry.suppress_unit_conversion else None

    @staticmethod
    def _read_transformation(entry: TmappingEntry) -> Ssp1Transformation | None:
        if entry.linear_transformation is not None:
            return Ssp1Transformation(
                type_name="LinearTransformation",
                attributes={
                    "factor": str(entry.linear_transformation.factor),
                    "offset": str(entry.linear_transformation.offset),
                },
            )
        if entry.boolean_mapping_transformation is not None:
            return Ssp1Transformation(type_name="BooleanMappingTransformation")
        if entry.integer_mapping_transformation is not None:
            return Ssp1Transformation(type_name="IntegerMappingTransformation")
        if entry.enumeration_mapping_transformation is not None:
            return Ssp1Transformation(type_name="EnumerationMappingTransformation")
        return None

    def _write_mapping_entry(self, entry: Ssp1MappingEntry) -> TmappingEntry:
        generated = TmappingEntry(
            source=entry.source,
            target=entry.target,
            suppress_unit_conversion=bool(entry.suppress_unit_conversion),
        )
        if entry.transformation is not None:
            self._apply_transformation(generated, entry.transformation)
        return generated

    @staticmethod
    def _apply_transformation(generated: TmappingEntry, transformation: Ssp1Transformation) -> None:
        attrs = transformation.attributes
        if transformation.type_name == "LinearTransformation":
            generated.linear_transformation = TmappingEntry.LinearTransformation(
                factor=_parse_numeric(attrs.get("factor"), default=1),
                offset=_parse_numeric(attrs.get("offset"), default=0),
            )
            return
        if transformation.type_name == "BooleanMappingTransformation":
            generated.boolean_mapping_transformation = TmappingEntry.BooleanMappingTransformation()
            return
        if transformation.type_name == "IntegerMappingTransformation":
            generated.integer_mapping_transformation = TmappingEntry.IntegerMappingTransformation()
            return
        if transformation.type_name == "EnumerationMappingTransformation":
            generated.enumeration_mapping_transformation = TmappingEntry.EnumerationMappingTransformation()
            return
        raise ValueError(f"Unsupported SSM transformation type '{transformation.type_name}'")


def _parse_numeric(value: str | None, *, default: int | float) -> int | float:
    if value is None or value == "":
        return default
    numeric = float(value)
    if numeric.is_integer() and "." not in value and "e" not in value.lower():
        return int(numeric)
    return numeric
