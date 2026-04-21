from __future__ import annotations

import shutil

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
        workdir = fmu._archive._workdir
        assert workdir is not None
        assert workdir.exists()
        assert (workdir / "modelDescription.xml").exists()

    assert archive._archive._workdir is None


def test_model_description_facade_reads_from_archive_contents(fmu_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        archive_xml = fmu._archive.read_text("modelDescription.xml")
        with fmu.model_description as md:
            assert len(md.inputs) > 0
            assert md.path.read_text(encoding="utf-8") == archive_xml
            assert md.check_compliance() is True
