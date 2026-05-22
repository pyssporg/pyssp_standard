from __future__ import annotations

import shutil
import zipfile

from pyssp_standard.common.archive import package_archive, unpack_archive


def test_package_archive_marks_library_files_executable(tmp_path):
    source_dir = tmp_path / "fmu"
    library_path = source_dir / "binaries" / "linux64" / "model.so"
    library_path.parent.mkdir(parents=True)
    library_path.write_bytes(b"library")
    library_path.chmod(0o644)

    archive_path = tmp_path / "model.fmu"
    package_archive(source_dir, archive_path)

    with zipfile.ZipFile(archive_path, "r") as archive:
        info = archive.getinfo("binaries/linux64/model.so")

    assert (info.external_attr >> 16) & 0o111


def test_unpack_archive_marks_library_files_executable(tmp_path):
    archive_path = tmp_path / "model.fmu"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("binaries/linux64/model.so", b"library")

    output_dir = tmp_path / "model"
    unpack_archive(archive_path, output_dir)

    assert (output_dir / "binaries" / "linux64" / "model.so").stat().st_mode & 0o111


def test_package_archive_can_pack_resource_fmu_directories_recursively(embrace_ssp_dir_fixture, tmp_path):
    source_dir = tmp_path / "embrace_dir"
    shutil.copytree(embrace_ssp_dir_fixture, source_dir)
    archive_path = tmp_path / "embrace.ssp"

    package_archive(source_dir, archive_path, recursive=True)

    with zipfile.ZipFile(archive_path, "r") as archive:
        names = set(archive.namelist())

    assert "resources/0001_ECS_HW.fmu" in names
    assert "resources/0001_ECS_HW/modelDescription.xml" not in names


def test_package_archive_packs_nested_resource_fmu_directories(embrace_ssp_dir_fixture, tmp_path):
    source_dir = tmp_path / "embrace_dir"
    shutil.copytree(embrace_ssp_dir_fixture, source_dir)
    nested_parent = source_dir / "resources" / "custom"
    nested_parent.mkdir()
    shutil.move(
        source_dir / "resources" / "0001_ECS_HW",
        nested_parent / "0001_ECS_HW",
    )
    archive_path = tmp_path / "embrace.ssp"

    package_archive(source_dir, archive_path, recursive=True)

    with zipfile.ZipFile(archive_path, "r") as archive:
        names = set(archive.namelist())

    assert "resources/custom/0001_ECS_HW.fmu" in names
    assert "resources/custom/0001_ECS_HW/modelDescription.xml" not in names


def test_package_archive_packs_nested_ssp_and_fmu_directories_recursively(embrace_ssp_dir_fixture, tmp_path):
    source_dir = tmp_path / "outer"
    nested_ssp_dir = source_dir / "resources" / "nested.ssp"
    shutil.copytree(embrace_ssp_dir_fixture, nested_ssp_dir)
    archive_path = tmp_path / "outer.ssp"

    package_archive(source_dir, archive_path, recursive=True)

    with zipfile.ZipFile(archive_path, "r") as outer_archive:
        outer_names = set(outer_archive.namelist())
        nested_ssp = outer_archive.read("resources/nested.ssp")

    assert "resources/nested.ssp" in outer_names
    assert "resources/nested.ssp/SystemStructure.ssd" not in outer_names

    nested_ssp_path = tmp_path / "nested.ssp"
    nested_ssp_path.write_bytes(nested_ssp)
    with zipfile.ZipFile(nested_ssp_path, "r") as nested_archive:
        nested_names = set(nested_archive.namelist())

    assert "SystemStructure.ssd" in nested_names
    assert "resources/0001_ECS_HW.fmu" in nested_names
    assert "resources/0001_ECS_HW/modelDescription.xml" not in nested_names


def test_unpack_archive_can_expand_nested_fmus_in_ssp(embrace_ssp_fixture, tmp_path):
    output_dir = tmp_path / "embrace_unpacked"

    unpack_archive(embrace_ssp_fixture, output_dir, recursive_fmus=True)

    assert (output_dir / "resources" / "0001_ECS_HW").is_dir()
    assert (output_dir / "resources" / "0001_ECS_HW" / "modelDescription.xml").is_file()
    assert not (output_dir / "resources" / "0001_ECS_HW.fmu").exists()
