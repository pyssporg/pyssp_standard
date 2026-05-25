"""Tests for set_generation_date_and_time across all 9 facades plus LS-REF exclusion."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

import pytest

from pyssp_standard.common.datetime_utils import format_generation_datetime
from pyssp_standard.md import ModelDescription
from pyssp_standard.ssb import SSB
from pyssp_standard.ssd import SSD
from pyssp_standard.ssm import SSM
from pyssp_standard.ssp import SSP
from pyssp_standard.ssv import SSV
from pyssp_standard.srmd import SRMD
from pyssp_standard.fmu import FMU
from pyssp_standard.ls_ref import LSRefExperiments, LSRefManifest


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------

class TestFormatGenerationDatetime:
    def test_none_returns_default(self):
        assert format_generation_datetime(None) == "2000-01-01T00:00:00Z"

    def test_datetime_formats_iso_8601(self):
        dt = datetime(2026, 4, 22, 12, 0, 0)
        assert format_generation_datetime(dt) == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self):
        raw = "2026-04-22T12:00:00Z"
        assert format_generation_datetime(raw) == raw

    def test_custom_datetime(self):
        dt = datetime(2025, 12, 31, 23, 59, 59)
        assert format_generation_datetime(dt) == "2025-12-31T23:59:59Z"


# ---------------------------------------------------------------------------
# XML document facades: SSD, SSV, SSB, SSM, SRMD
# All use self.xml.metadata.generation_date_and_time
# ---------------------------------------------------------------------------

class TestGenerationDateTimeSSD:

    def test_default_value(self, tmp_path):
        path = tmp_path / "test.ssd"
        with SSD(path, mode="w") as ssd:
            ssd.set_generation_date_and_time()
            assert ssd.xml.metadata.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "test.ssd"
        with SSD(path, mode="w") as ssd:
            ssd.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            assert ssd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "test.ssd"
        with SSD(path, mode="w") as ssd:
            ssd.set_generation_date_and_time("2026-04-22T12:00:00Z")
            assert ssd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path):
        path = tmp_path / "test.ssd"
        with SSD(path, mode="w") as ssd:
            ssd.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with SSD(path) as ssd:
            assert ssd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        ssd = SSD(tmp_path / "test.ssd")
        with pytest.raises(RuntimeError, match="not loaded"):
            ssd.set_generation_date_and_time()


class TestGenerationDateTimeSSV:

    def test_default_value(self, tmp_path):
        path = tmp_path / "test.ssv"
        with SSV(path, mode="w") as ssv:
            ssv.set_generation_date_and_time()
            assert ssv.xml.metadata.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "test.ssv"
        with SSV(path, mode="w") as ssv:
            ssv.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            assert ssv.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "test.ssv"
        with SSV(path, mode="w") as ssv:
            ssv.set_generation_date_and_time("2026-04-22T12:00:00Z")
            assert ssv.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path):
        path = tmp_path / "test.ssv"
        with SSV(path, mode="w") as ssv:
            ssv.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with SSV(path) as ssv:
            assert ssv.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        ssv = SSV(tmp_path / "test.ssv")
        with pytest.raises(RuntimeError, match="not loaded"):
            ssv.set_generation_date_and_time()


class TestGenerationDateTimeSSB:

    def test_default_value(self, tmp_path):
        path = tmp_path / "test.ssb"
        with SSB(path, mode="w") as ssb:
            ssb.set_generation_date_and_time()
            assert ssb.xml.metadata.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "test.ssb"
        with SSB(path, mode="w") as ssb:
            ssb.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            assert ssb.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "test.ssb"
        with SSB(path, mode="w") as ssb:
            ssb.set_generation_date_and_time("2026-04-22T12:00:00Z")
            assert ssb.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path):
        path = tmp_path / "test.ssb"
        with SSB(path, mode="w") as ssb:
            ssb.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with SSB(path) as ssb:
            assert ssb.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        ssb = SSB(tmp_path / "test.ssb")
        with pytest.raises(RuntimeError, match="not loaded"):
            ssb.set_generation_date_and_time()


class TestGenerationDateTimeSSM:

    def test_default_value(self, tmp_path):
        path = tmp_path / "test.ssm"
        with SSM(path, mode="w") as ssm:
            ssm.set_generation_date_and_time()
            assert ssm.xml.metadata.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "test.ssm"
        with SSM(path, mode="w") as ssm:
            ssm.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            assert ssm.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "test.ssm"
        with SSM(path, mode="w") as ssm:
            ssm.set_generation_date_and_time("2026-04-22T12:00:00Z")
            assert ssm.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path):
        path = tmp_path / "test.ssm"
        with SSM(path, mode="w") as ssm:
            ssm.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with SSM(path) as ssm:
            assert ssm.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        ssm = SSM(tmp_path / "test.ssm")
        with pytest.raises(RuntimeError, match="not loaded"):
            ssm.set_generation_date_and_time()


class TestGenerationDateTimeSRMD:

    def test_default_value(self, tmp_path):
        path = tmp_path / "test.srmd"
        with SRMD(path, mode="w") as srmd:
            srmd.set_generation_date_and_time()
            assert srmd.xml.metadata.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "test.srmd"
        with SRMD(path, mode="w") as srmd:
            srmd.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            assert srmd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "test.srmd"
        with SRMD(path, mode="w") as srmd:
            srmd.set_generation_date_and_time("2026-04-22T12:00:00Z")
            assert srmd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path):
        path = tmp_path / "test.srmd"
        with SRMD(path, mode="w") as srmd:
            srmd.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with SRMD(path) as srmd:
            assert srmd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        srmd = SRMD(tmp_path / "test.srmd")
        with pytest.raises(RuntimeError, match="not loaded"):
            srmd.set_generation_date_and_time()


# ---------------------------------------------------------------------------
# ModelDescription facade (FMI2 and FMI3)
# Uses self.xml.generation_date_and_time (direct, not through metadata)
# ---------------------------------------------------------------------------

class TestGenerationDateTimeModelDescriptionV2:

    _MINIMAL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription
  fmiVersion="2.0"
  modelName="Test"
  guid="{test-guid}">
  <CoSimulation modelIdentifier="Test" />
  <ModelVariables>
    <ScalarVariable name="x" valueReference="1"><Real /></ScalarVariable>
  </ModelVariables>
  <ModelStructure />
</fmiModelDescription>"""

    def test_default_value(self, tmp_path):
        path = tmp_path / "md.xml"
        path.write_text(self._MINIMAL_XML, encoding="utf-8")
        with ModelDescription(path, mode="a", version="2.0") as md:
            md.set_generation_date_and_time()
            assert md.xml.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "md.xml"
        path.write_text(self._MINIMAL_XML, encoding="utf-8")
        with ModelDescription(path, mode="a", version="2.0") as md:
            md.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "md.xml"
        path.write_text(self._MINIMAL_XML, encoding="utf-8")
        with ModelDescription(path, mode="a", version="2.0") as md:
            md.set_generation_date_and_time("2026-04-22T12:00:00Z")
            assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path):
        path = tmp_path / "md.xml"
        path.write_text(self._MINIMAL_XML, encoding="utf-8")
        with ModelDescription(path, mode="a", version="2.0") as md:
            md.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with ModelDescription(path, version="2.0") as md:
            assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        md = ModelDescription(tmp_path / "md.xml", version="2.0")
        with pytest.raises(RuntimeError, match="not loaded"):
            md.set_generation_date_and_time()


class TestGenerationDateTimeModelDescriptionV3:

    def test_default_value(self, tmp_path):
        path = tmp_path / "md.xml"
        with ModelDescription(path, mode="w", version="3.0") as md:
            md.set_generation_date_and_time()
            assert md.xml.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "md.xml"
        with ModelDescription(path, mode="w", version="3.0") as md:
            md.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "md.xml"
        with ModelDescription(path, mode="w", version="3.0") as md:
            md.set_generation_date_and_time("2026-04-22T12:00:00Z")
            assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path):
        path = tmp_path / "md.xml"
        with ModelDescription(path, mode="w", version="3.0") as md:
            md.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with ModelDescription(path, version="3.0") as md:
            assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        md = ModelDescription(tmp_path / "md.xml", version="3.0")
        with pytest.raises(RuntimeError, match="not loaded"):
            md.set_generation_date_and_time()


# ---------------------------------------------------------------------------
# Archive facades: SSP, FMU
# ---------------------------------------------------------------------------

class TestGenerationDateTimeSSP:

    def test_default_value(self, tmp_path):
        path = tmp_path / "test.ssp"
        with SSP(path, mode="w") as ssp:
            ssp.set_generation_date_and_time()
            with ssp.system_structure() as ssd:
                assert ssd.xml.metadata.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, tmp_path):
        path = tmp_path / "test.ssp"
        with SSP(path, mode="w") as ssp:
            ssp.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            with ssp.system_structure() as ssd:
                assert ssd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, tmp_path):
        path = tmp_path / "test.ssp"
        with SSP(path, mode="w") as ssp:
            ssp.set_generation_date_and_time("2026-04-22T12:00:00Z")
            with ssp.system_structure() as ssd:
                assert ssd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, tmp_path, embrace_ssp_dir_fixture):
        ssp_dir = tmp_path / "embrace_copy"
        shutil.copytree(embrace_ssp_dir_fixture, ssp_dir)
        with SSP(ssp_dir, mode="a") as ssp:
            ssp.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with SSP(ssp_dir, mode="r") as ssp:
            with ssp.system_structure() as ssd:
                assert ssd.xml.metadata.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, tmp_path):
        ssp = SSP(tmp_path / "test.ssp")
        with pytest.raises(RuntimeError, match="not open"):
            ssp.set_generation_date_and_time()


class TestGenerationDateTimeFMU:

    def test_default_value(self, fmu_directory_fixture, tmp_path):
        fmu_dir = tmp_path / "fmu_copy"
        shutil.copytree(fmu_directory_fixture, fmu_dir)
        with FMU(fmu_dir, mode="a") as fmu:
            fmu.set_generation_date_and_time()
            with fmu.model_description as md:
                assert md.xml.generation_date_and_time == "2000-01-01T00:00:00Z"

    def test_datetime_value(self, fmu_directory_fixture, tmp_path):
        fmu_dir = tmp_path / "fmu_copy"
        shutil.copytree(fmu_directory_fixture, fmu_dir)
        with FMU(fmu_dir, mode="a") as fmu:
            fmu.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
            with fmu.model_description as md:
                assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_string_passthrough(self, fmu_directory_fixture, tmp_path):
        fmu_dir = tmp_path / "fmu_copy"
        shutil.copytree(fmu_directory_fixture, fmu_dir)
        with FMU(fmu_dir, mode="a") as fmu:
            fmu.set_generation_date_and_time("2026-04-22T12:00:00Z")
            with fmu.model_description as md:
                assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_round_trip(self, fmu_directory_fixture, tmp_path):
        fmu_dir = tmp_path / "fmu_copy"
        shutil.copytree(fmu_directory_fixture, fmu_dir)
        with FMU(fmu_dir, mode="a") as fmu:
            fmu.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with FMU(fmu_dir, mode="r") as fmu:
            with fmu.model_description as md:
                assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_archive_round_trip(self, fmu_archive_fixture, tmp_path):
        fmu_path = tmp_path / "test.fmu"
        shutil.copy(fmu_archive_fixture, fmu_path)
        with FMU(fmu_path, mode="a") as fmu:
            fmu.set_generation_date_and_time(datetime(2026, 4, 22, 12, 0, 0))
        with FMU(fmu_path, mode="r") as fmu:
            with fmu.model_description as md:
                assert md.xml.generation_date_and_time == "2026-04-22T12:00:00Z"

    def test_runtime_error_outside_context(self, fmu_directory_fixture):
        fmu = FMU(fmu_directory_fixture)
        with pytest.raises(RuntimeError, match="not open"):
            fmu.set_generation_date_and_time()


# ---------------------------------------------------------------------------
# LS-REF exclusion — these facades do NOT have the method
# ---------------------------------------------------------------------------

class TestLSRefExclusion:

    def test_ls_ref_manifest_no_method(self):
        assert not hasattr(LSRefManifest, "set_generation_date_and_time")

    def test_ls_ref_experiments_no_method(self):
        assert not hasattr(LSRefExperiments, "set_generation_date_and_time")