from __future__ import annotations

import shutil
import zipfile

from pyssp_standard.fmu import FMU


def test_archive_lists_binary_and_documentation_entries(fmu_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        assert len(fmu.binaries) > 0
        assert all(entry.startswith("binaries/") for entry in fmu.binaries)
        assert len(fmu.documentation) > 0
        assert all(entry.startswith("documentation/") for entry in fmu.documentation)


def test_archive_uses_temp_workdir_and_cleans_up_after_exit(fmu_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_fixture, test_fmu_file)

    archive = FMU(test_fmu_file)
    with archive as fmu:
        root = fmu._archive.root
        assert root.exists()
        assert (root / "modelDescription.xml").exists()

    assert not root.exists()


def test_model_description_facade_reads_from_archive_contents(fmu_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        archive_xml = fmu._archive.read_text("modelDescription.xml")
        with fmu.model_description as md:
            assert len(md.inputs) > 0
            assert md.path.read_text(encoding="utf-8") == archive_xml
            assert md.check_compliance() is True


def test_directory_mode_reads_fmu_contents_from_persistent_root(fmu_fixture, tmp_path):
    unpacked_fmu_dir = tmp_path / "ecs_dir"
    unpacked_fmu_dir.mkdir()
    with zipfile.ZipFile(fmu_fixture, "r") as archive:
        archive.extractall(unpacked_fmu_dir)

    archive = FMU(unpacked_fmu_dir, mode="r")
    with archive as fmu:
        root = fmu._archive.root
        assert root == unpacked_fmu_dir
        assert "modelDescription.xml" in fmu._archive.namelist()
        assert len(fmu.binaries) > 0
        assert len(fmu.documentation) > 0

    assert root.exists()


def test_directory_mode_exposes_model_description(fmu_fixture, tmp_path):
    unpacked_fmu_dir = tmp_path / "ecs_dir"
    unpacked_fmu_dir.mkdir()
    with zipfile.ZipFile(fmu_fixture, "r") as archive:
        archive.extractall(unpacked_fmu_dir)

    with FMU(unpacked_fmu_dir, mode="r") as fmu:
        with fmu.model_description as md:
            assert len(md.inputs) > 0
            assert md.path == unpacked_fmu_dir / "modelDescription.xml"
