from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyssp_standard.common.xml_schema_validation import resolve_schema_path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SchemaTarget:
    name: str
    family: str
    version: str
    schema_path: Path


TARGETS: dict[str, SchemaTarget] = {
    "ssp1_ssv": SchemaTarget(
        name="ssp1_ssv",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureParameterValues.xsd"),
    ),
    "ssp1_ssd": SchemaTarget(
        name="ssp1_ssd",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureDescription.xsd"),
    ),
    "ssp1_ssb": SchemaTarget(
        name="ssp1_ssb",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureSignalDictionary.xsd"),
    ),
    "ssp1_ssm": SchemaTarget(
        name="ssp1_ssm",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureParameterMapping.xsd"),
    ),
    "ssp1_srmd": SchemaTarget(
        name="ssp1_srmd",
        family="SSP",
        version="1.0.0-beta2",
        schema_path=resolve_schema_path("SSP-LS-Traceability", "SRMD.xsd"),
    ),
    "ls_ref_manifest": SchemaTarget(
        name="ls_ref_manifest",
        family="FMI",
        version="1.0.0-alpha.1",
        schema_path=resolve_schema_path("FMI3", "fmi3LayeredStandardReferenceManifest.xsd"),
    ),
    "ls_ref_experiments": SchemaTarget(
        name="ls_ref_experiments",
        family="FMI",
        version="1.0.0-alpha.1",
        schema_path=resolve_schema_path("FMI3", "fmi3LayeredStandardReferenceExperiments.xsd"),
    ),
    "ssp2_ssv": SchemaTarget(
        name="ssp2_ssv",
        family="SSP",
        version="2.0",
        schema_path=resolve_schema_path("SSP2", "SystemStructureParameterValues.xsd"),
    ),
    "fmi2_model_description": SchemaTarget(
        name="fmi2_model_description",
        family="FMI",
        version="2.0",
        schema_path=resolve_schema_path("FMI2", "fmi2ModelDescription.xsd"),
    ),
    "fmi3_model_description": SchemaTarget(
        name="fmi3_model_description",
        family="FMI",
        version="3.0",
        schema_path=resolve_schema_path("FMI3", "fmi3ModelDescription.xsd"),
    ),
}
