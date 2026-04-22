from __future__ import annotations

import shutil
import zipfile

from pyssp_standard.fmu import FMU


def test_archive_lists_binary_and_documentation_entries(fmu_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_archive_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        assert len(fmu.binaries) > 0
        assert all(entry.startswith("binaries/") for entry in fmu.binaries)
        assert fmu.documentation == []


def test_archive_uses_temp_workdir_and_cleans_up_after_exit(fmu_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_archive_fixture, test_fmu_file)

    archive = FMU(test_fmu_file)
    with archive as fmu:
        root = fmu._archive.root
        assert root.exists()
        assert (root / "modelDescription.xml").exists()

    assert not root.exists()


def test_model_description_facade_reads_from_archive_contents(fmu_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_archive_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        archive_xml = fmu._archive.read_text("modelDescription.xml")
        with fmu.model_description as md:
            assert len(md.inputs) > 0
            assert md.path.read_text(encoding="utf-8") == archive_xml
            assert md.check_compliance() is True


def test_directory_mode_reads_fmu_contents_from_persistent_root(fmu_directory_fixture):
    archive = FMU(fmu_directory_fixture, mode="r")
    with archive as fmu:
        root = fmu._archive.root
        assert root == fmu_directory_fixture
        assert "modelDescription.xml" in fmu._archive.namelist()
        assert len(fmu.binaries) > 0
        assert len(fmu.documentation) == 0

    assert root.exists()


def test_directory_mode_exposes_model_description(fmu_directory_fixture):
    with FMU(fmu_directory_fixture, mode="r") as fmu:
        with fmu.model_description as md:
            assert len(md.inputs) > 0
            assert md.path == fmu_directory_fixture / "modelDescription.xml"


def test_archive_and_directory_modes_expose_same_model_name(fmu_archive_fixture, fmu_directory_fixture):
    with FMU(fmu_archive_fixture, mode="r") as archive_fmu:
        with archive_fmu.model_description as archive_md:
            archive_name = archive_md.document.model_name

    with FMU(fmu_directory_fixture, mode="r") as directory_fmu:
        with directory_fmu.model_description as directory_md:
            directory_name = directory_md.document.model_name

    assert archive_name == directory_name
