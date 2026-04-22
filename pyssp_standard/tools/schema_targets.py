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
    binding_output_path: Path


TARGETS: dict[str, SchemaTarget] = {
    "ssp1_ssv": SchemaTarget(
        name="ssp1_ssv",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureParameterValues.xsd"),
        binding_output_path=PACKAGE_ROOT / "standard" / "ssp1" / "generated" / "ssv_generated_types.py",
    ),
    "ssp1_ssd": SchemaTarget(
        name="ssp1_ssd",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureDescription.xsd"),
        binding_output_path=PACKAGE_ROOT / "standard" / "ssp1" / "generated" / "ssd_generated_types.py",
    ),
    "ssp1_ssb": SchemaTarget(
        name="ssp1_ssb",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureSignalDictionary.xsd"),
        binding_output_path=PACKAGE_ROOT / "standard" / "ssp1" / "generated" / "ssb_generated_types.py",
    ),
    "ssp1_ssm": SchemaTarget(
        name="ssp1_ssm",
        family="SSP",
        version="1.0",
        schema_path=resolve_schema_path("SSP1", "SystemStructureParameterMapping.xsd"),
        binding_output_path=PACKAGE_ROOT / "standard" / "ssp1" / "generated" / "ssm_generated_types.py",
    ),
    "ssp2_ssv": SchemaTarget(
        name="ssp2_ssv",
        family="SSP",
        version="2.0",
        schema_path=resolve_schema_path("SSP2", "SystemStructureParameterValues.xsd"),
        binding_output_path=PACKAGE_ROOT / "standard" / "ssp2" / "generated" / "ssv_generated_types.py",
    ),
    "fmi2_model_description": SchemaTarget(
        name="fmi2_model_description",
        family="FMI",
        version="2.0",
        schema_path=resolve_schema_path("FMI2", "fmi2ModelDescription.xsd"),
        binding_output_path=PACKAGE_ROOT / "standard" / "fmi2" / "generated" / "model_description_generated_types.py",
    ),
}
