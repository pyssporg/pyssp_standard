from __future__ import annotations

from pyssp_standard.tools.schema_targets import TARGETS


def test_schema_targets_have_separated_versioned_outputs():
    assert "ssp1_ssb" in TARGETS
    assert "ssp1_ssv" in TARGETS
    assert "ssp1_ssd" in TARGETS
    assert "ssp1_ssm" in TARGETS
    assert "ssp2_ssv" in TARGETS
    assert "fmi2_model_description" in TARGETS
    assert "ls_ref_manifest" in TARGETS
    assert "ls_ref_experiments" in TARGETS

    ssb = TARGETS["ssp1_ssb"]
    ssp1 = TARGETS["ssp1_ssv"]
    ssp2 = TARGETS["ssp2_ssv"]
    ssd = TARGETS["ssp1_ssd"]
    ssm = TARGETS["ssp1_ssm"]
    fmi2 = TARGETS["fmi2_model_description"]
    ls_ref_manifest = TARGETS["ls_ref_manifest"]
    ls_ref_experiments = TARGETS["ls_ref_experiments"]

    assert ssp1.family == "SSP"
    assert ssp2.family == "SSP"
    assert ssd.family == "SSP"
    assert ssm.family == "SSP"
    assert fmi2.family == "FMI"
    assert ls_ref_manifest.family == "FMI"
    assert ls_ref_experiments.family == "FMI"

    assert ssp1.version == "1.0"
    assert ssp2.version == "2.0"
    assert ssd.version == "1.0"
    assert ssm.version == "1.0"
    assert fmi2.version == "2.0"
    assert ls_ref_manifest.version == "1.0.0-alpha.1"
    assert ls_ref_experiments.version == "1.0.0-alpha.1"

    assert ssb.schema_path.name == "SystemStructureSignalDictionary.xsd"
    assert ssp1.schema_path.name == "SystemStructureParameterValues.xsd"
    assert ssp2.schema_path.name == "SystemStructureParameterValues.xsd"
    assert ssd.schema_path.name == "SystemStructureDescription.xsd"
    assert ssm.schema_path.name == "SystemStructureParameterMapping.xsd"
    assert fmi2.schema_path.name == "fmi2ModelDescription.xsd"
    assert ls_ref_manifest.schema_path.name == "fmi3LayeredStandardReferenceManifest.xsd"
    assert ls_ref_experiments.schema_path.name == "fmi3LayeredStandardReferenceExperiments.xsd"


def test_schema_target_paths_are_repo_relative():
    for target in TARGETS.values():
        assert target.schema_path.is_absolute()
        assert target.schema_path.exists()
        assert "pyssp_standard/schema" in target.schema_path.as_posix()
