from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from pyssp_standard.tools.xsdata_generation import TARGETS


@dataclass(frozen=True)
class StandardVersion:
    family: str
    format: str
    version: str


@dataclass(frozen=True)
class ParseStackSpec:
    standard: StandardVersion
    schema_path: Path
    generated_module: str
    generated_output_path: Path
    root_type: str
    codec_id: str
    mapper_id: str


CODEC_STACK: dict[StandardVersion, ParseStackSpec] = {
    StandardVersion(family="SSP", format="SSV", version="1.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSV", version="1.0"),
        schema_path=TARGETS["ssp1_ssv"].schema_path,
        generated_module="pyssp_standard.ssp1.generated.ssv_generated_types",
        generated_output_path=TARGETS["ssp1_ssv"].output_path,
        root_type="ParameterSet",
        codec_id="ssp1_ssv_xsdata_codec",
        mapper_id="ssp1_ssv_mapper",
    ),
    StandardVersion(family="SSP", format="SSV", version="2.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSV", version="2.0"),
        schema_path=TARGETS["ssp2_ssv"].schema_path,
        generated_module="pyssp_standard.ssp2.generated.ssv_generated_types",
        generated_output_path=TARGETS["ssp2_ssv"].output_path,
        root_type="ParameterSet",
        codec_id="ssp2_ssv_xsdata_codec",
        mapper_id="ssp2_ssv_mapper",
    ),
}


def get_standard_version(xml_text: str) -> StandardVersion:
    root = ET.fromstring(xml_text)
    version = root.attrib.get("version")

    if root.tag.startswith("{"):
        namespace, tag = root.tag[1:].split("}")
    else:
        namespace = None
        tag = root.tag

    if tag == "ParameterSet":
        return StandardVersion(family="SSP", format="SSV", version=version)
    # TODO: Implement the rest

    raise Exception("Standard not found")


def get_standard_version_from_file(path: Path) -> StandardVersion:
    return get_standard_version(path.read_text(encoding="utf-8"))


def get_parse_stack(standard: StandardVersion) -> ParseStackSpec:
    if standard not in CODEC_STACK:
        raise KeyError(
            f"No parse stack registered for ({standard.format}, {standard.family}, {standard.version})"
        )
    return CODEC_STACK[standard]


def get_parse_stack_from_xml(xml_text: str) -> ParseStackSpec:
    return get_parse_stack(get_standard_version(xml_text))


def get_parse_stack_from_file(path: Path) -> ParseStackSpec:
    return get_parse_stack(get_standard_version_from_file(path))
