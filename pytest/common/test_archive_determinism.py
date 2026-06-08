from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

import pytest

from pyssp_standard.common.archive import FMI_EPOCH, package_archive


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_source_dir(tmp_path: Path, name: str = "source") -> Path:
    d = tmp_path / name
    d.mkdir()
    (d / "modelDescription.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<fmiModelDescription fmiVersion="2.0" modelName="Test" guid="{g}">\n'
        "  <CoSimulation modelIdentifier=\"Test\" />\n"
        "  <ModelVariables>\n"
        '    <ScalarVariable name="x" valueReference="1"><Real/></ScalarVariable>\n'
        "  </ModelVariables>\n"
        "  <ModelStructure />\n"
        "</fmiModelDescription>\n",
    )
    (d / "resources").mkdir()
    (d / "resources" / "placeholder.txt").write_text("test content\n")
    return d


class TestArchiveDeterminism:
    def test_default_timestamp_is_backward_compatible(self, tmp_path):
        """fixed_timestamp=None produces a valid ZIP (backward compat)."""
        source = _make_source_dir(tmp_path, "s1")
        archive = tmp_path / "out.fmu"
        result = package_archive(source, archive)
        assert result == archive
        assert archive.exists()
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            assert "modelDescription.xml" in names

    def test_fixed_epoch_produces_consistent_timestamps(self, tmp_path):
        """With FMI_EPOCH, all entries have the same date_time."""
        source = _make_source_dir(tmp_path, "s2")
        archive = tmp_path / "out.fmu"
        package_archive(source, archive, fixed_timestamp=FMI_EPOCH)

        with zipfile.ZipFile(archive) as z:
            infos = z.infolist()
            assert len(infos) > 0
            timestamps = {info.date_time for info in infos}
            assert len(timestamps) == 1
            assert list(timestamps)[0] == FMI_EPOCH

    def test_same_source_same_timestamp_identical_hash(self, tmp_path):
        """Same source content + same fixed_timestamp → identical SHA256."""
        source1 = _make_source_dir(tmp_path, "a")
        archive1 = tmp_path / "a.fmu"
        package_archive(source1, archive1, fixed_timestamp=FMI_EPOCH)

        source2 = _make_source_dir(tmp_path, "b")
        archive2 = tmp_path / "b.fmu"
        package_archive(source2, archive2, fixed_timestamp=FMI_EPOCH)

        hash1 = _sha256(archive1)
        hash2 = _sha256(archive2)
        assert hash1 == hash2, f"Expected identical SHA256 but got {hash1} vs {hash2}"

    def test_different_source_same_timestamp_different_hash(self, tmp_path):
        """Different source content + same fixed_timestamp → different SHA256."""
        source_a = _make_source_dir(tmp_path, "a2")
        archive_a = tmp_path / "a2.fmu"
        package_archive(source_a, archive_a, fixed_timestamp=FMI_EPOCH)

        source_b = _make_source_dir(tmp_path, "b2")
        (source_b / "extra.txt").write_text("extra\n")
        archive_b = tmp_path / "b2.fmu"
        package_archive(source_b, archive_b, fixed_timestamp=FMI_EPOCH)

        assert _sha256(archive_a) != _sha256(archive_b)

    def test_default_timestamp_differs_from_fixed_epoch(self, tmp_path):
        """Default (filesystem) timestamps produce a different ZIP than FMI_EPOCH."""
        source_a = _make_source_dir(tmp_path, "d1")
        archive_a = tmp_path / "d1.fmu"
        package_archive(source_a, archive_a)
        hash_default = _sha256(archive_a)

        source_b = _make_source_dir(tmp_path, "d2")
        archive_b = tmp_path / "d2.fmu"
        package_archive(source_b, archive_b, fixed_timestamp=FMI_EPOCH)
        hash_fixed = _sha256(archive_b)

        # Timestamps will differ because filesystem mtime != FMI_EPOCH
        assert hash_default != hash_fixed

    def test_recursive_packaging_preserves_fixed_timestamp(self, tmp_path):
        """Nested FMU archives also use the fixed timestamp."""
        source = _make_source_dir(tmp_path, "parent")
        # Create a nested FMU directory
        nested_dir = source / "resources" / "nested.fmu"
        nested_dir.mkdir(parents=True)
        (nested_dir / "modelDescription.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<fmiModelDescription fmiVersion="2.0" modelName="Nested" guid="{n}">\n'
            "  <CoSimulation modelIdentifier=\"Nested\" />\n"
            "  <ModelVariables>\n"
            '    <ScalarVariable name="y" valueReference="2"><Real/></ScalarVariable>\n'
            "  </ModelVariables>\n"
            "  <ModelStructure />\n"
            "</fmiModelDescription>\n",
        )

        archive = tmp_path / "parent.ssp"
        package_archive(source, archive, recursive=True, fixed_timestamp=FMI_EPOCH)

        with zipfile.ZipFile(archive) as z:
            infos = z.infolist()
            for info in infos:
                assert info.date_time == FMI_EPOCH, (
                    f"Entry {info.filename} has timestamp {info.date_time}, expected {FMI_EPOCH}"
                )