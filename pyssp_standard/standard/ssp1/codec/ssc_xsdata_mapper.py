from __future__ import annotations

import copy
from xml.etree import ElementTree as ET

from xsdata.formats.dataclass.models.generics import AnyElement
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from pyssp_standard.standard.ssp1.generated.ssd_generated_types import Tconnectors
from pyssp_standard.standard.ssp1.generated.ssm_generated_types import TmappingEntry
from pyssp_standard.standard.ssp1.generated.ssv_generated_types import Tannotations as SsvTannotations, Tparameter, Tunit
from pyssp_standard.standard.ssp1.model.ssc_model import (
    Ssp1Annotation,
    Ssp1BaseUnit,
    Ssp1DocumentMetadata,
    Ssp1Transformation,
    Ssp1Unit,
)


class Ssp1SscXsdataMapper:
    _serializer = XmlSerializer(config=SerializerConfig(indent="  "))

    @staticmethod
    def read_document_metadata(generated: object) -> Ssp1DocumentMetadata:
        return Ssp1DocumentMetadata(
            id=getattr(generated, "id", None),
            description=getattr(generated, "description", None),
            author=getattr(generated, "author", None),
            fileversion=getattr(generated, "fileversion", None),
            copyright=getattr(generated, "copyright", None),
            license=getattr(generated, "license", None),
            generation_tool=getattr(generated, "generation_tool", None),
            generation_date_and_time=(
                str(getattr(generated, "generation_date_and_time", None))
                if getattr(generated, "generation_date_and_time", None) is not None
                else None
            ),
            annotations=Ssp1SscXsdataMapper.read_annotations(getattr(generated, "annotations", None)),
        )

    @staticmethod
    def write_document_metadata(metadata: Ssp1DocumentMetadata, *, annotations_cls) -> dict[str, object]:
        return {
            "id": metadata.id,
            "description": metadata.description,
            "author": metadata.author,
            "fileversion": metadata.fileversion,
            "copyright": metadata.copyright,
            "license": metadata.license,
            "generation_tool": metadata.generation_tool,
            "generation_date_and_time": metadata.generation_date_and_time,
            "annotations": Ssp1SscXsdataMapper.write_annotations(metadata.annotations, annotations_cls=annotations_cls),
        }

    @classmethod
    def read_annotations(cls, generated: object | None) -> list[Ssp1Annotation]:
        if generated is None:
            return []

        annotations: list[Ssp1Annotation] = []
        for entry in generated.annotation:
            elements = cls._normalize_wildcard(entry.any_element)
            annotations.append(Ssp1Annotation(type_name=entry.type_value, elements=elements))
        return annotations

    @staticmethod
    def write_annotations(annotations: list[Ssp1Annotation], *, annotations_cls) -> object | None:
        if not annotations:
            return None

        generated = annotations_cls()
        generated.annotation = [
            annotations_cls.Annotation(
                type_value=annotation.type_name,
                any_element=Ssp1SscXsdataMapper._write_annotation_payload(annotation.elements),
            )
            for annotation in annotations
        ]
        return generated

    @classmethod
    def _normalize_wildcard(cls, value: object) -> list[ET.Element]:
        if value is None:
            return []
        if isinstance(value, list):
            elements: list[ET.Element] = []
            for item in value:
                elements.extend(cls._normalize_wildcard(item))
            return elements
        if isinstance(value, ET.Element):
            return [copy.deepcopy(value)]
        if isinstance(value, AnyElement):
            return [cls._any_element_to_etree(value)]
        xml_text = cls._serializer.render(value)
        return [ET.fromstring(xml_text)]

    @staticmethod
    def _write_annotation_payload(elements: list[ET.Element]) -> object:
        if not elements:
            return None
        if len(elements) == 1:
            return Ssp1SscXsdataMapper._etree_to_any_element(elements[0])
        return [Ssp1SscXsdataMapper._etree_to_any_element(element) for element in elements]

    @staticmethod
    def _etree_to_any_element(element: ET.Element) -> AnyElement:
        return AnyElement(
            qname=element.tag,
            text=element.text,
            tail=element.tail,
            attributes=dict(element.attrib),
            children=[Ssp1SscXsdataMapper._etree_to_any_element(child) for child in list(element)],
        )

    @staticmethod
    def _any_element_to_etree(element: AnyElement) -> ET.Element:
        qname = element.qname or "value"
        generated = ET.Element(qname, attrib=element.attributes)
        generated.text = element.text
        generated.tail = element.tail
        for child in element.children:
            if isinstance(child, AnyElement):
                generated.append(Ssp1SscXsdataMapper._any_element_to_etree(child))
        return generated

    @staticmethod
    def read_unit(entry: Tunit) -> Ssp1Unit:
        base = entry.base_unit
        return Ssp1Unit(
            name=entry.name,
            id=entry.id,
            description=entry.description,
            annotations=Ssp1SscXsdataMapper.read_annotations(entry.annotations),
            base_unit=Ssp1BaseUnit(
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
    def write_unit(unit: Ssp1Unit) -> Tunit:
        return Tunit(
            name=unit.name,
            id=unit.id,
            description=unit.description,
            annotations=Ssp1SscXsdataMapper.write_annotations(unit.annotations, annotations_cls=SsvTannotations),
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
    def read_parameter_type(entry: Tparameter) -> tuple[str | None, dict[str, str]]:
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
    def write_parameter_type(name: str, type_name: str, attrs: dict[str, str]) -> Tparameter:
        if type_name == "Real":
            return Tparameter(
                name=name,
                real=Tparameter.Real(
                    value=float(attrs.get("value", "0.0")),
                    unit=attrs.get("unit"),
                ),
            )
        if type_name == "Integer":
            return Tparameter(name=name, integer=Tparameter.Integer(value=int(attrs.get("value", "0"))))
        if type_name == "Boolean":
            value = attrs.get("value", "false").lower() in {"true", "1"}
            return Tparameter(name=name, boolean=Tparameter.Boolean(value=value))
        if type_name == "String":
            return Tparameter(name=name, string=Tparameter.String(value=attrs.get("value", "")))
        if type_name == "Enumeration":
            return Tparameter(
                name=name,
                enumeration=Tparameter.Enumeration(
                    value=attrs.get("value", ""),
                    name=attrs.get("name"),
                ),
            )
        if type_name == "Binary":
            value = bytes.fromhex(attrs.get("value", "")) if attrs.get("value") else b""
            return Tparameter(
                name=name,
                binary=Tparameter.Binary(value=value, mime_type=attrs.get("mime-type", "application/octet-stream")),
            )
        raise ValueError(f"Unsupported SSV1 parameter type '{type_name}'")

    @staticmethod
    def read_connector_type(generated: Tconnectors.Connector) -> tuple[str | None, dict[str, str]]:
        type_name = None
        type_attributes: dict[str, str] = {}

        if generated.real is not None:
            type_name = "Real"
            if generated.real.unit is not None:
                type_attributes["unit"] = generated.real.unit
        elif generated.integer is not None:
            type_name = "Integer"
        elif generated.boolean is not None:
            type_name = "Boolean"
        elif generated.string is not None:
            type_name = "String"
        elif generated.enumeration is not None:
            type_name = "Enumeration"
            type_attributes["name"] = generated.enumeration.name
        elif generated.binary is not None:
            type_name = "Binary"
            type_attributes["mime-type"] = generated.binary.mime_type

        return type_name, type_attributes

    @staticmethod
    def apply_connector_type(generated: Tconnectors.Connector, type_name: str | None, attrs: dict[str, str]) -> None:
        if type_name == "Real":
            generated.real = Tconnectors.Connector.Real(unit=attrs.get("unit"))
        elif type_name == "Integer":
            generated.integer = ""
        elif type_name == "Boolean":
            generated.boolean = ""
        elif type_name == "String":
            generated.string = ""
        elif type_name == "Enumeration":
            generated.enumeration = Tconnectors.Connector.Enumeration(name=attrs.get("name", ""))
        elif type_name == "Binary":
            generated.binary = Tconnectors.Connector.Binary(
                mime_type=attrs.get("mime-type", "application/octet-stream")
            )

    @staticmethod
    def read_transformation(entry: TmappingEntry) -> Ssp1Transformation | None:
        if entry.linear_transformation is not None:
            return Ssp1Transformation(
                type_name="LinearTransformation",
                attributes={
                    "factor": str(entry.linear_transformation.factor),
                    "offset": str(entry.linear_transformation.offset),
                },
            )
        if entry.boolean_mapping_transformation is not None:
            return Ssp1Transformation(type_name="BooleanMappingTransformation", attributes={})
        if entry.integer_mapping_transformation is not None:
            return Ssp1Transformation(type_name="IntegerMappingTransformation", attributes={})
        if entry.enumeration_mapping_transformation is not None:
            return Ssp1Transformation(type_name="EnumerationMappingTransformation", attributes={})
        return None

    @staticmethod
    def apply_transformation(generated: TmappingEntry, transformation: Ssp1Transformation) -> None:
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
