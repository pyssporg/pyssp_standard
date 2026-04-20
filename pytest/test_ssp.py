import shutil
import tempfile
from pathlib import Path

import pytest

from pyssp_standard.ssp import SSP


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace.ssp")


@pytest.fixture
def write_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.close()
        yield f.name


def test_unpacking_lists_existing_resources(read_file):
    with SSP(read_file, mode="r") as ssp:
        assert len(ssp.resources) > 0
        assert "0001_ECS_HW.fmu" in ssp.resources


def test_add_resource_persists_to_archive(read_file, tmp_path):
    test_ssp_file = tmp_path / "embrace.ssp"
    shutil.copy(read_file, test_ssp_file)
    file_to_add = Path("pytest/doc/test.txt")

    with SSP(test_ssp_file) as ssp:
        added_name = ssp.add_resource(file_to_add)
        assert added_name == file_to_add.name
        assert file_to_add.name in ssp.resources

    with SSP(test_ssp_file, mode="r") as ssp:
        assert file_to_add.name in ssp.resources


def test_remove_resource_persists_to_archive(read_file, tmp_path):
    test_ssp_file = tmp_path / "embrace.ssp"
    shutil.copy(read_file, test_ssp_file)

    with SSP(test_ssp_file) as ssp:
        file_to_remove = ssp.resources[0]
        ssp.remove_resource(file_to_remove)
        assert file_to_remove not in ssp.resources

    with SSP(test_ssp_file, mode="r") as ssp:
        assert file_to_remove not in ssp.resources


def test_create_empty_ssp_archive(write_file):
    with SSP(write_file, mode="w") as ssp:
        assert isinstance(ssp, SSP)
        assert ssp.resources == []

    assert Path(write_file).exists()


def test_ssp_archive_uses_temp_workdir_while_open_and_cleans_up_after_exit(read_file):
    archive = SSP(read_file, mode="r")

    with archive as ssp:
        workdir = ssp._archive._workdir
        assert workdir is not None
        assert workdir.exists()
        assert (workdir / "SystemStructure.ssd").exists()

    assert archive._archive._workdir is None


@pytest.mark.xfail(strict=True, reason="SSP.system_structure facade is not implemented yet")
def test_ssp_exposes_system_structure_from_archive(read_file):
    with SSP(read_file, mode="r") as ssp:
        with ssp.system_structure as ssd:
            assert ssd is not None


@pytest.mark.xfail(strict=True, reason="SSP should expose the extracted SSD through a stable path/context")
def test_ssp_system_structure_points_at_extracted_archive_file(read_file):
    with SSP(read_file, mode="r") as ssp:
        system_structure = ssp.system_structure
        assert system_structure.exists()
        assert system_structure.name == "SystemStructure.ssd"
        assert system_structure.read_text(encoding="utf-8").startswith("<?xml")


@pytest.mark.xfail(strict=True, reason="SSP create mode does not yet scaffold a usable package structure")
def test_create_mode_scaffolds_system_structure_entry(write_file):
    with SSP(write_file, mode="w") as ssp:
        _ = ssp.system_structure

    with SSP(write_file, mode="r") as ssp:
        assert "SystemStructure.ssd" in ssp._archive.namelist()
