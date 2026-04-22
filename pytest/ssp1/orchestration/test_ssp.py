from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest

from pyssp_standard.fmu import FMU
from pyssp_standard.ssd import SSD
from pyssp_standard.ssp import SSP
from pyssp_standard.ssv import SSV


def test_lists_existing_resources(embrace_ssp_dir_fixture):
    with SSP(embrace_ssp_dir_fixture, mode="r") as ssp:
        assert len(ssp.resources) > 0
        assert "0001_ECS_HW/modelDescription.xml" in ssp.resources
        assert "0002_ECS_SW.fmu" in ssp.resources


def test_add_resource_persists_to_archive(embrace_ssp_archive_fixture, tmp_path):
    test_ssp_file = tmp_path / "embrace.ssp"
    shutil.copy(embrace_ssp_archive_fixture, test_ssp_file)
    file_to_add = Path("pytest/__fixture__/test.txt")

    with SSP(test_ssp_file) as ssp:
        added_name = ssp.add_resource(file_to_add)
        assert added_name == file_to_add.name
        assert file_to_add.name in ssp.resources

    with SSP(test_ssp_file, mode="r") as ssp:
        assert file_to_add.name in ssp.resources


def test_remove_resource_persists_to_archive(embrace_ssp_archive_fixture, tmp_path):
    test_ssp_file = tmp_path / "embrace.ssp"
    shutil.copy(embrace_ssp_archive_fixture, test_ssp_file)

    with SSP(test_ssp_file) as ssp:
        file_to_remove = ssp.resources[0]
        ssp.remove_resource(file_to_remove)
        assert file_to_remove not in ssp.resources

    with SSP(test_ssp_file, mode="r") as ssp:
        assert file_to_remove not in ssp.resources


@pytest.fixture
def write_file():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.close()
        yield file.name


def test_create_empty_archive(write_file):
    with SSP(write_file, mode="w") as ssp:
        assert isinstance(ssp, SSP)
        assert ssp.resources == []

    assert Path(write_file).exists()


def test_archive_uses_temp_workdir_and_cleans_up_after_exit(embrace_ssp_archive_fixture):
    archive = SSP(embrace_ssp_archive_fixture, mode="r")

    with archive as ssp:
        root = ssp._archive.root
        assert root.exists()

    assert not root.exists()


def test_system_structure_uses_extracted_archive_file(embrace_ssp_archive_fixture):
    with SSP(embrace_ssp_archive_fixture, mode="r") as ssp:
        system_structure = ssp.system_structure()
        assert system_structure.path.exists()
        assert system_structure.path.name == "SystemStructure.ssd"
        assert system_structure.path.read_text(encoding="utf-8").startswith("<?xml")


def test_create_mode_scaffolds_system_structure_entry(write_file):
    with SSP(write_file, mode="w") as ssp:
        facade = ssp.system_structure()
        assert not facade.path.exists()
        with facade:
            assert facade.path.exists() is False

    with SSP(write_file, mode="r") as ssp:
        assert "SystemStructure.ssd" in ssp._archive.namelist()


def test_directory_mode_uses_persistent_root_and_keeps_it_after_exit(embrace_ssd_fixture, tmp_path):
    unpacked_ssp_dir = tmp_path / "embrace_dir"
    shutil.copytree(embrace_ssd_fixture.parent, unpacked_ssp_dir)

    archive = SSP(unpacked_ssp_dir, mode="r")
    with archive as ssp:
        root = ssp._archive.root
        assert root == unpacked_ssp_dir
        assert root.exists()

    assert root.exists()


def test_directory_add_resource_persists_without_repacking(embrace_ssd_fixture, tmp_path):
    unpacked_ssp_dir = tmp_path / "embrace_dir"
    shutil.copytree(embrace_ssd_fixture.parent, unpacked_ssp_dir)
    file_to_add = Path("pytest/__fixture__/test.txt")

    with SSP(unpacked_ssp_dir, mode="a") as ssp:
        added_name = ssp.add_resource(file_to_add)
        assert added_name == file_to_add.name
        assert (unpacked_ssp_dir / "resources" / file_to_add.name).exists()

    with SSP(unpacked_ssp_dir, mode="r") as ssp:
        assert file_to_add.name in ssp.resources


def test_directory_write_mode_scaffolds_system_structure(tmp_path):
    unpacked_ssp_dir = tmp_path / "new_ssp_dir"

    with SSP(unpacked_ssp_dir, mode="w") as ssp:
        facade = ssp.system_structure()
        assert not facade.path.exists()
        with facade:
            assert facade.path.exists() is False

    assert (unpacked_ssp_dir / "SystemStructure.ssd").exists()


def test_directory_system_structure_uses_fixture_file_directly(embrace_ssp_dir_fixture):
    with SSP(embrace_ssp_dir_fixture, mode="r") as ssp:
        facade = ssp.system_structure()
        assert facade.path == embrace_ssp_dir_fixture / "SystemStructure.ssd"
        assert facade.path.exists()


def test_can_open_model_description_from_directory_backed_fmu_inside_directory_ssp(
    embrace_ssp_fixture,
):
    with SSP(embrace_ssp_fixture, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            component = next(component for component in ssd.system.elements if component.name == "ECS_HW")
            assert component.source == "resources/0001_ECS_HW.fmu"

            with FMU(ssp.runtime.resolve(component.source), mode="r") as fmu:
                with fmu.model_description as md:
                    assert md.document.model_name == "ECS_HW"
                    assert len(md.inputs) > 0



def test_can_open_and_alter_model_description_from_directory_backed_fmu_inside_directory_ssp(
    embrace_ssp_fixture,
):
    with SSP(embrace_ssp_fixture, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            component = next(component for component in ssd.system.elements if component.name == "ECS_HW")
            assert component.source == "resources/0001_ECS_HW.fmu"

            with FMU(ssp.runtime.resolve(component.source), mode="r") as fmu:
                with fmu.model_description as md:
                    assert md.document.model_name == "ECS_HW"
                    assert len(md.inputs) > 0


def test_resolves_external_parameter_bindings_at_archive_layer(tmp_path):
    ssp_path = tmp_path / "mixed.ssp"
    with zipfile.ZipFile(ssp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write("pytest/__fixture__/mixed_example.ssd", arcname="SystemStructure.ssd")
        archive.write("pytest/__fixture__/external_values.ssv", arcname="external_values.ssv")

    with SSD("pytest/__fixture__/mixed_example.ssd") as standalone_ssd:
        external_binding = next(binding for binding in standalone_ssd.parameter_bindings if binding.source is not None)
        assert external_binding.parameter_set is None

    with SSP(ssp_path, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            external_binding = next(binding for binding in ssd.parameter_bindings if binding.source is not None)
            assert external_binding.parameter_set is not None
            assert external_binding.parameter_set.name == "ControllerExternal"
            assert external_binding.parameter_set.parameters[0].attributes["value"] == "0.8"
            assert external_binding.parameter_mapping is None


def test_persists_resolved_external_parameter_sets(tmp_path):
    ssp_path = tmp_path / "mixed.ssp"
    with zipfile.ZipFile(ssp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write("pytest/__fixture__/mixed_example.ssd", arcname="SystemStructure.ssd")
        archive.write("pytest/__fixture__/external_values.ssv", arcname="external_values.ssv")

    with SSP(ssp_path, mode="a") as ssp:
        with ssp.system_structure() as ssd:
            external_binding = next(binding for binding in ssd.parameter_bindings if binding.source is not None)
            external_binding.parameter_set.parameters[0].attributes["value"] = "1.25"

    with SSP(ssp_path, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            external_binding = next(binding for binding in ssd.parameter_bindings if binding.source is not None)
            assert external_binding.parameter_set is not None
            assert external_binding.parameter_set.parameters[0].attributes["value"] == "1.25"

    extracted_ssv = tmp_path / "external_values.ssv"
    with zipfile.ZipFile(ssp_path, "r") as archive:
        archive.extract("external_values.ssv", path=tmp_path)
    with SSV(extracted_ssv) as ssv:
        assert ssv.parameters[0].attributes["value"] == "1.25"


def test_resolves_external_parameter_mapping_at_archive_layer(embrace_ssp_dir_fixture):
    with SSP(embrace_ssp_dir_fixture, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            binding = ssd.parameter_bindings[0]
            assert binding.source == "resources/RAPID_Systems_2021-03-29_Test_1.ssv"
            assert binding.parameter_set is not None
            assert len(binding.parameter_set.parameters) > 0
            assert binding.parameter_mapping is not None
            assert binding.parameter_mapping.source == "resources/ECS_HW.ssm"
            assert binding.parameter_mapping.mapping is not None
            assert len(binding.parameter_mapping.mapping.mappings) > 0
