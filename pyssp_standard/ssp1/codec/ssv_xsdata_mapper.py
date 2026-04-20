from __future__ import annotations

from pyssp_standard.ssp1.generated.ssv_generated_types import ParameterSet, Tparameter, Tparameters, Tunits, Tunit
from pyssp_standard.ssp1.model.ssv_model import (
    SsvBaseUnit,
    SsvDocumentMetadata,
    SsvParameter,
    SsvParameterSet,
    SsvUnit,
)


class Ssp1SsvXsdataMapper:
    
    def read_parameterset(self, generated: ParameterSet) -> SsvParameterSet:
        parameters: list[SsvParameter] = []
        for entry in generated.parameters.parameter:
            ptype, attrs = self._read_parameter(entry)
            if ptype is None:
                continue
            parameters.append(SsvParameter(name=entry.name, type_name=ptype, attributes=attrs))

        units = [self._read_unit(entry) for entry in generated.units.unit] if generated.units is not None else []

        metadata = SsvDocumentMetadata(
            id=generated.id,
            description=generated.description,
            author=generated.author,
            fileversion=generated.fileversion,
            copyright=generated.copyright,
            license=generated.license,
            generation_tool=generated.generation_tool,
            generation_date_and_time=str(generated.generation_date_and_time)
            if generated.generation_date_and_time is not None
            else None,
        )

        return SsvParameterSet(
            name=generated.name,
            version=generated.version,
            metadata=metadata,
            parameters=parameters,
            units=units,
        )

    def write_parameterset(self, model: SsvParameterSet) -> ParameterSet:
        units = Tunits(unit=[self._write_unit(unit) for unit in model.units]) if model.units else None
        return ParameterSet(
            version=model.version,
            name=model.name,
            parameters=Tparameters(parameter=[self._write_parameter(param) for param in model.parameters]),
            units=units,
            id=model.metadata.id,
            description=model.metadata.description,
            author=model.metadata.author,
            fileversion=model.metadata.fileversion,
            copyright=model.metadata.copyright,
            license=model.metadata.license,
            generation_tool=model.metadata.generation_tool,
            generation_date_and_time=model.metadata.generation_date_and_time,
        )

    @staticmethod
    def _read_unit(entry: Tunit) -> SsvUnit:
        base = entry.base_unit
        return SsvUnit(
            name=entry.name,
            id=entry.id,
            description=entry.description,
            base_unit=SsvBaseUnit(
                kg=base.kg,
                m=base.m,
                s=base.s,
                a=base.a,
                k=base.k,
                mol=base.mol,
                cd=base.cd,
                rad=base.rad,
                factor=base.factor,
                offset=base.offset,
            ),
        )

    @staticmethod
    def _write_unit(unit: SsvUnit) -> Tunit:
        return Tunit(
            name=unit.name,
            id=unit.id,
            description=unit.description,
            base_unit=Tunit.BaseUnit(
                kg=unit.base_unit.kg or 0,
                m=unit.base_unit.m or 0,
                s=unit.base_unit.s or 0,
                a=unit.base_unit.a or 0,
                k=unit.base_unit.k or 0,
                mol=unit.base_unit.mol or 0,
                cd=unit.base_unit.cd or 0,
                rad=unit.base_unit.rad or 0,
                factor=unit.base_unit.factor if unit.base_unit.factor is not None else 1.0,
                offset=unit.base_unit.offset if unit.base_unit.offset is not None else 0.0,
            ),
        )

    @staticmethod
    def _read_parameter(entry: Tparameter) -> tuple[str | None, dict[str, str]]:
        if entry.real is not None:
            attrs = {"value": str(entry.real.value)}
            if entry.real.unit is not None:
                attrs["unit"] = entry.real.unit
            return "Real", attrs
        if entry.integer is not None:
            return "Integer", {"value": str(entry.integer.value)}
        if entry.boolean is not None:
            return "Boolean", {"value": str(entry.boolean.value).lower()}
        if entry.string is not None:
            return "String", {"value": entry.string.value}
        if entry.enumeration is not None:
            attrs = {"value": entry.enumeration.value}
            if entry.enumeration.name is not None:
                attrs["name"] = entry.enumeration.name
            return "Enumeration", attrs
        if entry.binary is not None:
            attrs = {"value": entry.binary.value.hex()}
            if entry.binary.mime_type is not None:
                attrs["mime-type"] = entry.binary.mime_type
            return "Binary", attrs
        return None, {}

    @staticmethod
    def _write_parameter(param: SsvParameter) -> Tparameter:
        attrs = param.attributes
        if param.type_name == "Real":
            return Tparameter(
                name=param.name,
                real=Tparameter.Real(
                    value=float(attrs.get("value", "0.0")),
                    unit=attrs.get("unit"),
                ),
            )
        if param.type_name == "Integer":
            return Tparameter(name=param.name, integer=Tparameter.Integer(value=int(attrs.get("value", "0"))))
        if param.type_name == "Boolean":
            value = attrs.get("value", "false").lower() in {"true", "1"}
            return Tparameter(name=param.name, boolean=Tparameter.Boolean(value=value))
        if param.type_name == "String":
            return Tparameter(name=param.name, string=Tparameter.String(value=attrs.get("value", "")))
        if param.type_name == "Enumeration":
            return Tparameter(
                name=param.name,
                enumeration=Tparameter.Enumeration(
                    value=attrs.get("value", ""),
                    name=attrs.get("name"),
                ),
            )
        if param.type_name == "Binary":
            value = bytes.fromhex(attrs.get("value", "")) if attrs.get("value") else b""
            return Tparameter(
                name=param.name,
                binary=Tparameter.Binary(value=value, mime_type=attrs.get("mime-type", "application/octet-stream")),
            )

        raise ValueError(f"Unsupported SSV1 parameter type '{param.type_name}'")
