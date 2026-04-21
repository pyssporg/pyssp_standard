from __future__ import annotations

from pathlib import Path

import pytest


FIXTURE_DIR = Path("pytest/__fixture__")


@pytest.fixture
def embrace_ssd_fixture() -> Path:
    return FIXTURE_DIR / "embrace" / "SystemStructure.ssd"


@pytest.fixture
def embrace_ssm_fixture() -> Path:
    return FIXTURE_DIR / "embrace" / "resources" / "ECS_HW.ssm"


@pytest.fixture
def embrace_ssp_fixture() -> Path:
    return FIXTURE_DIR / "embrace.ssp"


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
    return FIXTURE_DIR / "embrace" / "fmu" / "modelDescription.xml"


@pytest.fixture
def fmu_fixture() -> Path:
    return FIXTURE_DIR / "embrace" / "resources" / "0001_ECS_HW.fmu"


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
