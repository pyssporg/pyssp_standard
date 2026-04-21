from __future__ import annotations

from pathlib import Path

from pyssp_standard.tools.xsdata_generation import TARGETS


def test_generation_targets_have_separated_versioned_outputs():
    assert "ssp1_ssv" in TARGETS
    assert "ssp2_ssv" in TARGETS

    ssp1 = TARGETS["ssp1_ssv"]
    ssp2 = TARGETS["ssp2_ssv"]

    assert ssp1.output_path != ssp2.output_path
    assert "ssp1/generated" in str(ssp1.output_path)
    assert "ssp2/generated" in str(ssp2.output_path)
    assert ssp1.schema_path.name == "SystemStructureParameterValues.xsd"
    assert ssp2.schema_path.name == "SystemStructureParameterValues.xsd"


def test_generation_target_paths_are_repo_relative():
    for target in TARGETS.values():
        assert target.schema_path.is_absolute()
        assert target.output_path.is_absolute()
        assert target.schema_path.exists()
        assert target.output_path.parent.exists() or Path(target.output_path.parent).is_absolute()
