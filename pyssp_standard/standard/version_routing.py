from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from pyssp_standard.standard.fmi2.codec.model_description_xml_codec import (
    Fmi2ModelDescriptionXmlCodec,
)
from pyssp_standard.standard.fmi2.validation.model_description_validation import (
    Fmi2ModelDescriptionValidator,
)
from pyssp_standard.standard.fmi3.codec.model_description_xml_codec import (
    Fmi3ModelDescriptionXmlCodec,
)
from pyssp_standard.standard.fmi3.validation.model_description_validation import (
    Fmi3ModelDescriptionValidator,
)
from pyssp_standard.standard.ls_ref.codec import (
    LSRefExperimentsCodec,
    LSRefManifestCodec,
)
from pyssp_standard.standard.ls_ref.constants import (
    DEFAULT_LS_REF_VERSION,
    FMI_LS_MANIFEST_NAMESPACE,
)
from pyssp_standard.standard.ls_ref.validation import (
    LSRefExperimentsValidator,
    LSRefManifestValidator,
)
from pyssp_standard.standard.ssp1.codec.ssb_codec import Ssp1SsbCodec
from pyssp_standard.standard.ssp1.codec.ssd_codec import Ssp1SsdCodec
from pyssp_standard.standard.ssp1.codec.ssm_codec import Ssp1SsmCodec
from pyssp_standard.standard.ssp1.codec.srmd_codec import Ssp1SrmdCodec
from pyssp_standard.standard.ssp1.codec.ssv_codec import Ssp1SsvCodec
from pyssp_standard.standard.ssp2.codec.ssv_codec import Ssp2SsvCodec
from pyssp_standard.standard.ssp2.validation.ssv_validation import Ssp2SsvValidator
from pyssp_standard.standard.ssp1.validation.ssb_validation import Ssp1SsbValidator
from pyssp_standard.standard.ssp1.validation.ssd_validation import Ssp1SsdValidator
from pyssp_standard.standard.ssp1.validation.ssm_validation import Ssp1SsmValidator
from pyssp_standard.standard.ssp1.validation.srmd_validation import Ssp1SrmdValidator
from pyssp_standard.standard.ssp1.validation.ssv_validation import Ssp1SsvValidator
from pyssp_standard.tools.schema_targets import TARGETS


@dataclass(frozen=True)
class StandardVersion:
    family: str
    format: str
    version: str


@dataclass(frozen=True)
class ParseStackSpec:
    standard: StandardVersion
    schema_path: Path
    codec_type: type[Any] | None = None
    validator_type: type[Any] | None = None


CODEC_STACK: dict[StandardVersion, ParseStackSpec] = {
    StandardVersion(family="SSP", format="SSB", version="1.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSB", version="1.0"),
        schema_path=TARGETS["ssp1_ssb"].schema_path,
        codec_type=Ssp1SsbCodec,
        validator_type=Ssp1SsbValidator,
    ),
    StandardVersion(family="SSP", format="SSV", version="1.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSV", version="1.0"),
        schema_path=TARGETS["ssp1_ssv"].schema_path,
        codec_type=Ssp1SsvCodec,
        validator_type=Ssp1SsvValidator,
    ),
    StandardVersion(family="SSP", format="SSD", version="1.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSD", version="1.0"),
        schema_path=TARGETS["ssp1_ssd"].schema_path,
        codec_type=Ssp1SsdCodec,
        validator_type=Ssp1SsdValidator,
    ),
    StandardVersion(family="SSP", format="SSM", version="1.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSM", version="1.0"),
        schema_path=TARGETS["ssp1_ssm"].schema_path,
        codec_type=Ssp1SsmCodec,
        validator_type=Ssp1SsmValidator,
    ),
    StandardVersion(family="SSP", format="SRMD", version="1.0.0-beta2"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SRMD", version="1.0.0-beta2"),
        schema_path=TARGETS["ssp1_srmd"].schema_path,
        codec_type=Ssp1SrmdCodec,
        validator_type=Ssp1SrmdValidator,
    ),
    StandardVersion(family="FMI", format="LS-REF-MANIFEST", version="1.0.0-alpha.1"): ParseStackSpec(
        standard=StandardVersion(family="FMI", format="LS-REF-MANIFEST", version="1.0.0-alpha.1"),
        schema_path=TARGETS["ls_ref_manifest"].schema_path,
        codec_type=LSRefManifestCodec,
        validator_type=LSRefManifestValidator,
    ),
    StandardVersion(family="FMI", format="LS-REF-EXPERIMENTS", version="1.0.0-alpha.1"): ParseStackSpec(
        standard=StandardVersion(family="FMI", format="LS-REF-EXPERIMENTS", version="1.0.0-alpha.1"),
        schema_path=TARGETS["ls_ref_experiments"].schema_path,
        codec_type=LSRefExperimentsCodec,
        validator_type=LSRefExperimentsValidator,
    ),
    StandardVersion(family="SSP", format="SSV", version="2.0"): ParseStackSpec(
        standard=StandardVersion(family="SSP", format="SSV", version="2.0"),
        schema_path=TARGETS["ssp2_ssv"].schema_path,
        codec_type=Ssp2SsvCodec,
        validator_type=Ssp2SsvValidator,
    ),
    StandardVersion(family="FMI", format="MD", version="2.0"): ParseStackSpec(
        standard=StandardVersion(family="FMI", format="MD", version="2.0"),
        schema_path=TARGETS["fmi2_model_description"].schema_path,
        codec_type=Fmi2ModelDescriptionXmlCodec,
        validator_type=Fmi2ModelDescriptionValidator,
    ),
    StandardVersion(family="FMI", format="MD", version="3.0"): ParseStackSpec(
        standard=StandardVersion(family="FMI", format="MD", version="3.0"),
        schema_path=TARGETS["fmi3_model_description"].schema_path,
        codec_type=Fmi3ModelDescriptionXmlCodec,
        validator_type=Fmi3ModelDescriptionValidator,
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
    if tag == "SignalDictionary":
        return StandardVersion(family="SSP", format="SSB", version=version)
    if tag == "SystemStructureDescription":
        return StandardVersion(family="SSP", format="SSD", version=version)
    if tag == "ParameterMapping":
        return StandardVersion(family="SSP", format="SSM", version=version)
    if tag == "SimulationResourceMetaData":
        return StandardVersion(family="SSP", format="SRMD", version=version)
    if tag == "fmiReferences":
        return StandardVersion(
            family="FMI",
            format="LS-REF-MANIFEST",
            version=root.attrib.get(f"{{{FMI_LS_MANIFEST_NAMESPACE}}}fmi-ls-version", DEFAULT_LS_REF_VERSION),
        )
    if tag == "Experiments":
        return StandardVersion(family="FMI", format="LS-REF-EXPERIMENTS", version=DEFAULT_LS_REF_VERSION)
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


def get_codec_and_validator(standard: StandardVersion) -> tuple[type[Any] | None, type[Any] | None]:
    """Resolve codec and validator types for a given standard version."""
    spec = get_parse_stack(standard)
    return spec.codec_type, spec.validator_type
