import shutil
from pathlib import Path

import pytest

from pyssp_standard.fmu import FMU


@pytest.fixture
def fmu_file():
    return Path("pytest/doc/embrace/resources/0001_ECS_HW.fmu")


def test_fmu_archive_lists_binary_and_documentation_entries(fmu_file, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_file, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        assert len(fmu.binaries) > 0
        assert all(entry.startswith("binaries/") for entry in fmu.binaries)
        assert len(fmu.documentation) > 0
        assert all(entry.startswith("documentation/") for entry in fmu.documentation)


def test_fmu_archive_uses_temp_workdir_while_open_and_cleans_up_after_exit(fmu_file, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_file, test_fmu_file)

    archive = FMU(test_fmu_file)
    with archive as fmu:
        workdir = fmu._archive._workdir
        assert workdir is not None
        assert workdir.exists()
        assert (workdir / "modelDescription.xml").exists()

    assert archive._archive._workdir is None


@pytest.mark.xfail(strict=True, reason="FMU.model_description facade is not implemented yet")
def test_fmu_exposes_loaded_model_description_via_public_property(fmu_file, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_file, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        with fmu.model_description as md:
            assert md is not None
            assert len(md.inputs) > 0


@pytest.mark.xfail(strict=True, reason="FMU facade does not yet expose archive XML through a stable path/context")
def test_fmu_model_description_round_trips_from_archive_contents(fmu_file, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_file, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        archive_xml = fmu._archive.read_text("modelDescription.xml")
        with fmu.model_description as md:
            parsed_xml = md.path.read_text(encoding="utf-8")

    assert parsed_xml == archive_xml
