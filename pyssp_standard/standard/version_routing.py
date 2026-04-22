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
        generated_module="pyssp_standard.standard.ssp1.generated.ssv_generated_types",
        generated_output_path=TARGETS["ssp1_ssv"].output_path,
        root_type="ParameterSet",
        codec_id="ssp1_ssv_xsdata_codec",
        mapper_id="ssp1_ssv_mapper",
    ),
    StandardVersion(family="SSP", format="SSD", version="1.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSD", version="1.0"),
        schema_path=TARGETS["ssp1_ssd"].schema_path,
        generated_module="pyssp_standard.standard.ssp1.generated.ssd_generated_types",
        generated_output_path=TARGETS["ssp1_ssd"].output_path,
        root_type="SystemStructureDescription",
        codec_id="ssp1_ssd_xsdata_codec",
        mapper_id="ssp1_ssd_mapper",
    ),
    StandardVersion(family="SSP", format="SSM", version="1.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSM", version="1.0"),
        schema_path=TARGETS["ssp1_ssm"].schema_path,
        generated_module="pyssp_standard.standard.ssp1.generated.ssm_generated_types",
        generated_output_path=TARGETS["ssp1_ssm"].output_path,
        root_type="ParameterMapping",
        codec_id="ssp1_ssm_xsdata_codec",
        mapper_id="ssp1_ssm_mapper",
    ),
    StandardVersion(family="SSP", format="SSV", version="2.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSV", version="2.0"),
        schema_path=TARGETS["ssp2_ssv"].schema_path,
        generated_module="pyssp_standard.standard.ssp2.generated.ssv_generated_types",
        generated_output_path=TARGETS["ssp2_ssv"].output_path,
        root_type="ParameterSet",
        codec_id="ssp2_ssv_xsdata_codec",
        mapper_id="ssp2_ssv_mapper",
    ),
    StandardVersion(family="FMI", format="MD", version="2.0"): ParseStackSpec(
        standard=StandardVersion(family="FMI", format="MD", version="2.0"),
        schema_path=TARGETS["fmi2_model_description"].schema_path,
        generated_module="pyssp_standard.standard.fmi2.generated.model_description_generated_types",
        generated_output_path=TARGETS["fmi2_model_description"].output_path,
        root_type="FmiModelDescription",
        codec_id="fmi2_model_description_xsdata_codec",
        mapper_id="fmi2_model_description_mapper",
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
    if tag == "SystemStructureDescription":
        return StandardVersion(family="SSP", format="SSD", version=version)
    if tag == "ParameterMapping":
        return StandardVersion(family="SSP", format="SSM", version=version)
    if tag == "fmiModelDescription":
        return StandardVersion(family="FMI", format="MD", version=root.attrib.get("fmiVersion"))

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
