from __future__ import annotations

from pathlib import Path
import shutil
import zipfile

import pytest


FIXTURE_DIR = Path("pytest/__fixture__")
EMBRACE_DIR = FIXTURE_DIR / "embrace"


def _write_zip_from_tree(source_dir: Path, target_file: Path) -> Path:
    with zipfile.ZipFile(target_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(source_dir).as_posix())
    return target_file


@pytest.fixture
def embrace_ssd_fixture() -> Path:
    return EMBRACE_DIR / "SystemStructure.ssd"


@pytest.fixture
def embrace_ssm_fixture() -> Path:
    return EMBRACE_DIR / "resources" / "ECS_HW.ssm"


@pytest.fixture
def embrace_ssp_dir_fixture() -> Path:
    return EMBRACE_DIR


@pytest.fixture
def embrace_ssp_fixture(tmp_path: Path, embrace_ssp_dir_fixture: Path) -> Path:
    ssp_dir = tmp_path / "embrace_dir"
    shutil.copytree(embrace_ssp_dir_fixture, ssp_dir)

    fmu_dir = ssp_dir / "resources" / "0001_ECS_HW"
    fmu_path = ssp_dir / "resources" / "0001_ECS_HW.fmu"
    _write_zip_from_tree(fmu_dir, fmu_path)
    shutil.rmtree(fmu_dir)

    ssp_path = tmp_path / "embrace.ssp"
    return _write_zip_from_tree(ssp_dir, ssp_path)


@pytest.fixture
def embrace_ssp_archive_fixture(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return _write_zip_from_tree(EMBRACE_DIR, tmp_path_factory.mktemp("ssp_archive") / "embrace.ssp")


@pytest.fixture
def mixed_ssd_fixture() -> Path:
    return FIXTURE_DIR / "mixed_example.ssd"


@pytest.fixture
def external_ssv_fixture() -> Path:
    return FIXTURE_DIR / "external_values.ssv"


@pytest.fixture
def ssv2_fixture() -> Path:
    return FIXTURE_DIR / "ssv2_ex.ssv"


@pytest.fixture
def model_description_fixture() -> Path:
    return EMBRACE_DIR / "resources" / "0001_ECS_HW" / "modelDescription.xml"


@pytest.fixture
def fmu_directory_fixture() -> Path:
    return EMBRACE_DIR / "resources" / "0001_ECS_HW"


@pytest.fixture
def fmu_archive_fixture(tmp_path_factory: pytest.TempPathFactory, fmu_directory_fixture: Path) -> Path:
    return _write_zip_from_tree(fmu_directory_fixture, tmp_path_factory.mktemp("fmu_archive") / "0001_ECS_HW.fmu")


def pytest_collection_modifyitems(config, items):
    path_markers = {
        "codec": pytest.mark.codec,
        "facade": pytest.mark.facade,
        "archive": pytest.mark.archive,
        "orchestration": pytest.mark.archive,
        "tools": pytest.mark.tooling,
        "demo": pytest.mark.demo,
    }

    for item in items:
        parts = Path(str(item.fspath)).parts
        for path_part, marker in path_markers.items():
            if path_part in parts:
                item.add_marker(marker)
