from __future__ import annotations

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from pyssp_standard.ssp1.model.ssv_model import SsvParameter, SsvParameterSet
from pyssp_standard.ssp2.generated.ssv_generated_types import ParameterSet, Tparameter, Tparameters


NS_SSV = "http://ssp-standard.org/SSP1/SystemStructureParameterValues"


class Ssp2SsvXsdataCodec:
    def __init__(self):
        self._parser = XmlParser()
        self._serializer = XmlSerializer(config=SerializerConfig(indent="  "))

    def parse(self, xml_text: str) -> SsvParameterSet:
        generated = self._parser.from_string(xml_text, ParameterSet)
        parameters: list[SsvParameter] = []

        for entry in generated.parameters.parameter:
            ptype, attrs = self._read_parameter(entry)
            if ptype is None:
                continue
            parameters.append(SsvParameter(name=entry.name, type_name=ptype, attributes=attrs))

        return SsvParameterSet(
            name=generated.name,
            version=generated.version,
            parameters=parameters,
        )

    def serialize(self, model: SsvParameterSet) -> str:
        generated = ParameterSet(
            version=model.version,
            name=model.name,
            parameters=Tparameters(parameter=[self._write_parameter(param) for param in model.parameters]),
        )
        return self._serializer.render(generated, ns_map={"ssv": NS_SSV})

    @staticmethod
    def _join(values: list[object]) -> str:
        return " ".join(str(value) for value in values)

    @classmethod
    def _read_parameter(cls, entry: Tparameter) -> tuple[str | None, dict[str, str]]:
        if entry.real is not None:
            attrs = {"value": cls._join(entry.real.value)}
            if entry.real.unit is not None:
                attrs["unit"] = entry.real.unit
            return "Real", attrs
        if entry.float64 is not None:
            attrs = {"value": cls._join(entry.float64.value)}
            if entry.float64.unit is not None:
                attrs["unit"] = entry.float64.unit
            return "Float64", attrs
        if entry.float32 is not None:
            attrs = {"value": cls._join(entry.float32.value)}
            if entry.float32.unit is not None:
                attrs["unit"] = entry.float32.unit
            return "Float32", attrs
        if entry.integer is not None:
            return "Integer", {"value": cls._join(entry.integer.value)}
        if entry.int8 is not None:
            return "Int8", {"value": cls._join(entry.int8.value)}
        if entry.uint8 is not None:
            return "UInt8", {"value": cls._join(entry.uint8.value)}
        if entry.int16 is not None:
            return "Int16", {"value": cls._join(entry.int16.value)}
        if entry.uint16 is not None:
            return "UInt16", {"value": cls._join(entry.uint16.value)}
        if entry.int32 is not None:
            return "Int32", {"value": cls._join(entry.int32.value)}
        if entry.uint32 is not None:
            return "UInt32", {"value": cls._join(entry.uint32.value)}
        if entry.int64 is not None:
            return "Int64", {"value": cls._join(entry.int64.value)}
        if entry.uint64 is not None:
            return "UInt64", {"value": cls._join(entry.uint64.value)}
        if entry.boolean is not None:
            return "Boolean", {"value": " ".join("true" if value else "false" for value in entry.boolean.value)}
        if entry.string is not None:
            return "String", {"value": " ".join(entry.string.value)}
        if entry.enumeration is not None:
            attrs = {"value": cls._join(entry.enumeration.value)}
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
    def _split_tokens(value: str) -> list[str]:
        return [token for token in value.split() if token]

    @classmethod
    def _write_parameter(cls, param: SsvParameter) -> Tparameter:
        attrs = param.attributes
        values = cls._split_tokens(attrs.get("value", ""))

        if param.type_name == "Real":
            return Tparameter(name=param.name, real=Tparameter.Real(value=[float(v) for v in values or ["0.0"]], unit=attrs.get("unit")))
        if param.type_name == "Float64":
            return Tparameter(name=param.name, float64=Tparameter.Float64(value=[float(v) for v in values or ["0.0"]], unit=attrs.get("unit")))
        if param.type_name == "Float32":
            return Tparameter(name=param.name, float32=Tparameter.Float32(value=[float(v) for v in values or ["0.0"]], unit=attrs.get("unit")))
        if param.type_name == "Integer":
            return Tparameter(name=param.name, integer=Tparameter.Integer(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "Int8":
            return Tparameter(name=param.name, int8=Tparameter.Int8(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "UInt8":
            return Tparameter(name=param.name, uint8=Tparameter.Uint8(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "Int16":
            return Tparameter(name=param.name, int16=Tparameter.Int16(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "UInt16":
            return Tparameter(name=param.name, uint16=Tparameter.Uint16(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "Int32":
            return Tparameter(name=param.name, int32=Tparameter.Int32(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "UInt32":
            return Tparameter(name=param.name, uint32=Tparameter.Uint32(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "Int64":
            return Tparameter(name=param.name, int64=Tparameter.Int64(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "UInt64":
            return Tparameter(name=param.name, uint64=Tparameter.Uint64(value=[int(v) for v in values or ["0"]]))
        if param.type_name == "Boolean":
            bool_values = [(v.lower() in {"true", "1"}) for v in values or ["false"]]
            return Tparameter(name=param.name, boolean=Tparameter.Boolean(value=bool_values))
        if param.type_name == "String":
            return Tparameter(name=param.name, string=Tparameter.String(value=values or [""]))
        if param.type_name == "Enumeration":
            return Tparameter(
                name=param.name,
                enumeration=Tparameter.Enumeration(value=values or [""], name=attrs.get("name")),
            )
        if param.type_name == "Binary":
            value = bytes.fromhex(attrs.get("value", "")) if attrs.get("value") else b""
            return Tparameter(
                name=param.name,
                binary=Tparameter.Binary(value=value, mime_type=attrs.get("mime-type", "application/octet-stream")),
            )

        raise ValueError(f"Unsupported SSV2 parameter type '{param.type_name}'")
