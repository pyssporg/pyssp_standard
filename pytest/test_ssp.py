import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest

from pyssp_standard.ssp import SSP
from pyssp_standard.ssv import SSV


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


def test_ssp_exposes_system_structure_from_archive(read_file):
    with SSP(read_file, mode="r") as ssp:
        with ssp.system_structure as ssd:
            assert ssd is not None


def test_ssp_system_structure_uses_extracted_archive_file(read_file):
    with SSP(read_file, mode="r") as ssp:
        system_structure = ssp.system_structure
        assert system_structure.path.exists()
        assert system_structure.path.name == "SystemStructure.ssd"
        assert system_structure.path.read_text(encoding="utf-8").startswith("<?xml")


def test_create_mode_scaffolds_system_structure_entry(write_file):
    with SSP(write_file, mode="w") as ssp:
        _ = ssp.system_structure

    with SSP(write_file, mode="r") as ssp:
        assert "SystemStructure.ssd" in ssp._archive.namelist()


def test_ssp_orchestrates_external_parameter_bindings(tmp_path):
    ssp_path = tmp_path / "mixed.ssp"
    with zipfile.ZipFile(ssp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write("pytest/doc/mixed_example.ssd", arcname="SystemStructure.ssd")
        archive.write("pytest/doc/external_values.ssv", arcname="external_values.ssv")

    # Standalone SSD does not resolve external references automatically.
    from pyssp_standard.ssd import SSD

    with SSD("pytest/doc/mixed_example.ssd") as standalone_ssd:
        external_binding = next(binding for binding in standalone_ssd.parameter_bindings if not binding.is_inlined)
        assert external_binding.parameter_set is None
        assert external_binding.is_resolved is False

    # SSP owns archive-relative orchestration and resolves the external SSV.
    with SSP(ssp_path, mode="r") as ssp:
        with ssp.system_structure as ssd:
            external_binding = next(binding for binding in ssd.parameter_bindings if not binding.is_inlined)
            assert external_binding.parameter_set is not None
            assert external_binding.parameter_set.name == "ControllerExternal"
            assert external_binding.parameter_set.parameters[0].attributes["value"] == "0.8"
            assert external_binding.is_resolved is True
            assert external_binding.parameter_mapping is None


def test_ssp_persists_resolved_external_parameter_sets(tmp_path):
    ssp_path = tmp_path / "mixed.ssp"
    with zipfile.ZipFile(ssp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write("pytest/doc/mixed_example.ssd", arcname="SystemStructure.ssd")
        archive.write("pytest/doc/external_values.ssv", arcname="external_values.ssv")

    with SSP(ssp_path, mode="a") as ssp:
        with ssp.system_structure as ssd:
            external_binding = next(binding for binding in ssd.parameter_bindings if not binding.is_inlined)
            external_binding.parameter_set.parameters[0].attributes["value"] = "1.25"

    with SSP(ssp_path, mode="r") as ssp:
        with ssp.system_structure as ssd:
            external_binding = next(binding for binding in ssd.parameter_bindings if not binding.is_inlined)
            assert external_binding.parameter_set is not None
            assert external_binding.parameter_set.parameters[0].attributes["value"] == "1.25"

    # Standalone SSV stays a plain file facade: it loads the referenced file directly,
    # but it does not participate in cross-file resolution on its own.
    extracted_ssv = tmp_path / "external_values.ssv"
    with zipfile.ZipFile(ssp_path, "r") as archive:
        archive.extract("external_values.ssv", path=tmp_path)
    with SSV(extracted_ssv) as ssv:
        assert ssv.parameters[0].attributes["value"] == "1.25"


def test_ssp_orchestrates_external_parameter_mapping_resolution(read_file):
    with SSP(read_file, mode="r") as ssp:
        with ssp.system_structure as ssd:
            binding = ssd.parameter_bindings[0]
            assert binding.external_path == "resources/RAPID_Systems_2021-03-29_Test_1.ssv"
            assert binding.parameter_set is None
            assert binding.is_resolved is False
            assert binding.parameter_mapping_path == "resources/ECS_HW.ssm"
            assert binding.parameter_mapping is not None
            assert len(binding.parameter_mapping.mappings) > 0
            assert binding.is_mapping_resolved is True
