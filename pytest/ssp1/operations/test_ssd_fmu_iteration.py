"""Tests for SSD FMU iteration operations."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyssp_standard.fmu import FMU
from pyssp_standard.common.directory_runtime import DirectoryRuntime
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1System,
)
from pyssp_standard.standard.ssp1.operations.ssd_fmu_iteration import (
    FmuEntry,
    iter_fmu_entries,
)
from pyssp_standard.ssp import SSP


# ---------------------------------------------------------------------------
# Helper to build a DirectoryRuntime over a tmp_path
# ---------------------------------------------------------------------------

@pytest.fixture
def runtime(tmp_path: Path) -> DirectoryRuntime:
    r = DirectoryRuntime(tmp_path, mode="a")
    r.__enter__()
    yield r
    r.__exit__(None, None, None)


# ---------------------------------------------------------------------------
# Flat iteration (non-recursive) — direct components only
# ---------------------------------------------------------------------------

class TestFlatIteration:
    def test_flat_iteration_yields_direct_components(self, runtime: DirectoryRuntime):
        c1 = Ssd1Component(name="A", source="a.fmu")
        c2 = Ssd1Component(name="B", source="b.fmu")
        system = Ssd1System(name="root", elements=[c1, c2])

        Path(runtime.resolve("a.fmu")).touch()
        Path(runtime.resolve("b.fmu")).touch()

        entries = list(iter_fmu_entries(system, runtime))
        assert len(entries) == 2
        assert {e.component.name for e in entries} == {"A", "B"}

    def test_empty_system_yields_nothing(self, runtime: DirectoryRuntime):
        system = Ssd1System(name="root", elements=[])
        entries = list(iter_fmu_entries(system, runtime))
        assert entries == []

    def test_system_with_only_subsystems_non_recursive(self, runtime: DirectoryRuntime):
        inner_comp = Ssd1Component(name="Inner", source="inner.fmu")
        subsystem = Ssd1System(name="sub", elements=[inner_comp])
        system = Ssd1System(name="root", elements=[subsystem])

        Path(runtime.resolve("inner.fmu")).touch()

        entries = list(iter_fmu_entries(system, runtime))
        assert entries == []


# ---------------------------------------------------------------------------
# Recursive iteration
# ---------------------------------------------------------------------------

class TestRecursiveIteration:
    def test_recursive_iteration_yields_nested_components(self, runtime: DirectoryRuntime):
        inner = Ssd1Component(name="Inner", source="inner.fmu")
        subsystem = Ssd1System(name="sub", elements=[inner])
        outer = Ssd1Component(name="Outer", source="outer.fmu")
        system = Ssd1System(name="root", elements=[outer, subsystem])

        Path(runtime.resolve("inner.fmu")).touch()
        Path(runtime.resolve("outer.fmu")).touch()

        entries = list(iter_fmu_entries(system, runtime, recursive=True))
        names = {e.component.name for e in entries}
        assert names == {"Inner", "Outer"}
        assert len(entries) == 2


# ---------------------------------------------------------------------------
# skip_missing behaviour
# ---------------------------------------------------------------------------

class TestSkipMissing:
    def test_skip_missing_true_skips_nonexistent_source(self, runtime: DirectoryRuntime):
        c1 = Ssd1Component(name="Exists", source="exists.fmu")
        c2 = Ssd1Component(name="Missing", source="missing.fmu")
        system = Ssd1System(name="root", elements=[c1, c2])

        Path(runtime.resolve("exists.fmu")).touch()
        # missing.fmu deliberately not created

        entries = list(iter_fmu_entries(system, runtime, skip_missing=True))
        assert len(entries) == 1
        assert entries[0].component.name == "Exists"

    def test_skip_missing_false_yields_missing_source(self, runtime: DirectoryRuntime):
        c1 = Ssd1Component(name="Exists", source="exists.fmu")
        c2 = Ssd1Component(name="Missing", source="missing.fmu")
        system = Ssd1System(name="root", elements=[c1, c2])

        Path(runtime.resolve("exists.fmu")).touch()

        entries = list(iter_fmu_entries(system, runtime, skip_missing=False))
        assert len(entries) == 2
        names = {e.component.name for e in entries}
        assert names == {"Exists", "Missing"}


# ---------------------------------------------------------------------------
# FmuEntry dataclass / open_fmu
# ---------------------------------------------------------------------------

class TestFmuEntry:
    def test_open_fmu_opens_fmu_from_entry(
        self, runtime: DirectoryRuntime, fmu_archive_fixture: Path
    ):
        """FmuEntry.open_fmu() returns a usable FMU instance."""
        resource_path = fmu_archive_fixture.name
        resolved = runtime.resolve(resource_path)

        # Copy the real FMU archive into the runtime root
        import shutil
        shutil.copy2(fmu_archive_fixture, resolved)

        component = Ssd1Component(name="TestFMU", source=resource_path)
        entry = FmuEntry(component=component, source=resolved, resource_path=resource_path)

        with entry.open_fmu() as fmu:
            assert isinstance(fmu, FMU)
            # Verify we can introspect the FMU
            with fmu.model_description as md:
                assert md.xml.model_name is not None

    def test_fmu_entry_fields(self, runtime: DirectoryRuntime):
        """Verify FmuEntry source, component, resource_path are correct."""
        component = Ssd1Component(name="MyComp", source="resources/my.fmu")
        source_path = runtime.resolve("resources/my.fmu")
        Path(source_path).parent.mkdir(parents=True, exist_ok=True)
        Path(source_path).touch()

        system = Ssd1System(name="root", elements=[component])
        entries = list(iter_fmu_entries(system, runtime))
        assert len(entries) == 1
        entry = entries[0]

        assert entry.component is component
        assert entry.source == source_path
        assert entry.resource_path == "resources/my.fmu"


# ---------------------------------------------------------------------------
# Standalone usage (without SSP)
# ---------------------------------------------------------------------------

class TestStandalone:
    def test_standalone_function_without_ssp(self, tmp_path: Path):
        """Direct call to iter_fmu_entries with constructed model + DirectoryRuntime."""
        runtime = DirectoryRuntime(tmp_path, mode="a")
        runtime.__enter__()
        try:
            comp = Ssd1Component(name="Direct", source="direct.fmu")
            system = Ssd1System(name="root", elements=[comp])

            Path(runtime.resolve("direct.fmu")).touch()
            entries = list(iter_fmu_entries(system, runtime))
            assert len(entries) == 1
            assert entries[0].component.name == "Direct"
        finally:
            runtime.__exit__(None, None, None)


# ---------------------------------------------------------------------------
# Source type variants
# ---------------------------------------------------------------------------

class TestSourceVariants:
    def test_fmu_archive_source(
        self, runtime: DirectoryRuntime, fmu_archive_fixture: Path
    ):
        """Component source points to a .fmu archive file."""
        import shutil
        shutil.copy2(fmu_archive_fixture, runtime.resolve(fmu_archive_fixture.name))

        component = Ssd1Component(
            name="ArchiveFMU", source=fmu_archive_fixture.name
        )
        system = Ssd1System(name="root", elements=[component])

        entries = list(iter_fmu_entries(system, runtime))
        assert len(entries) == 1
        assert entries[0].source.suffix == ".fmu"

    def test_fmu_directory_source(
        self, runtime: DirectoryRuntime, fmu_directory_fixture: Path
    ):
        """Component source points to an extracted FMU directory."""
        import shutil
        dst = runtime.resolve("0001_ECS_HW")
        shutil.copytree(fmu_directory_fixture, dst)

        component = Ssd1Component(name="DirFMU", source="0001_ECS_HW")
        system = Ssd1System(name="root", elements=[component])

        entries = list(iter_fmu_entries(system, runtime))
        assert len(entries) == 1
        assert entries[0].source.is_dir()


# ---------------------------------------------------------------------------
# SSP-delegated usage
# ---------------------------------------------------------------------------

class TestSspDelegated:
    def test_ssp_delegated_usage(self, tmp_path: Path, fmu_archive_fixture: Path):
        """Via SSP.iter_fmu_entries() with a minimal tmpdir-based SSP."""
        import shutil

        ssp_dir = tmp_path / "my_ssp"
        ssp_dir.mkdir()

        resources_dir = ssp_dir / "resources"
        resources_dir.mkdir()

        # Place the FMU archive in resources/
        shutil.copy2(fmu_archive_fixture, resources_dir / fmu_archive_fixture.name)

        # Write a minimal SystemStructure.ssd
        ssd_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ssd:SystemStructureDescription
  xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon"
  xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructureDescription"
  name="test_ssp"
  version="1.0">
  <ssd:System name="system">
    <ssd:Elements>
      <ssd:Component name="ECS_HW" source="resources/{fmu_archive_fixture.name}">
        <ssd:Connectors/>
      </ssd:Component>
    </ssd:Elements>
  </ssd:System>
</ssd:SystemStructureDescription>
"""
        (ssp_dir / "SystemStructure.ssd").write_text(ssd_xml)

        with SSP(ssp_dir, mode="r") as ssp:
            entries = list(ssp.iter_fmu_entries())
            assert len(entries) == 1
            entry = entries[0]
            assert entry.component.name == "ECS_HW"
            assert entry.source.name == fmu_archive_fixture.name

            # Verify we can open the FMU via the entry
            with entry.open_fmu() as fmu:
                assert isinstance(fmu, FMU)