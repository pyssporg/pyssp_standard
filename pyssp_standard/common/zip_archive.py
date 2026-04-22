from __future__ import annotations

from pathlib import Path

import tempfile
import zipfile

from pyssp_standard.common.directory_runtime import DirectoryRuntime

class ZipArchive:
    """Shared archive-layer helper for .ssp and .fmu zip containers."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None
        self._runtime = DirectoryRuntime(self.path, mode)

    def __enter__(self) -> "ZipArchive":
        if self.mode not in {"r", "a", "w"}:
            raise ValueError(f"Unsupported archive mode '{self.mode}'")

        if self.mode == "r" and not self.path.exists():
            raise FileNotFoundError(f"Archive does not exist: {self.path}")

        self._temp_dir = tempfile.TemporaryDirectory(prefix=f"{self.path.stem}_archive_")
        self._runtime = DirectoryRuntime(self._temp_dir.name, mode="a")
        self._runtime.__enter__()

        if self.mode in {"r", "a"} and self.path.exists() and self.path.stat().st_size > 0:
            with zipfile.ZipFile(self.path, "r") as archive:
                archive.extractall(self.root)
        return self._runtime

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None and self.mode in {"w", "a"}:
                self._commit()
            return False
        finally:
            self._runtime.__exit__(exc_type, exc, tb)
            if self._temp_dir is not None:
                self._temp_dir.cleanup()
                self._temp_dir = None

    @property
    def root(self) -> Path:
        return self._runtime.root

    def namelist(self) -> list[str]:
        return self._runtime.namelist()

    def read_text(self, name: str, encoding: str = "utf-8") -> str:
        return self._runtime.read_text(name, encoding=encoding)

    def add_file(self, source: str | Path, target_name: str | None = None) -> str:
        return self._runtime.add_file(source, target_name=target_name)

    def remove_file(self, target_name: str) -> None:
        self._runtime.remove_file(target_name)

    def list_prefix(self, prefix: str) -> list[str]:
        return self._runtime.list_prefix(prefix)

    def _commit(self) -> None:
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for entry in sorted(self.root.rglob("*")):
                if entry.is_file():
                    archive.write(entry, arcname=entry.relative_to(self.root).as_posix())


def open_archive(path: str | Path, mode: str = "r") -> DirectoryRuntime | ZipArchive:
    resolved_path = Path(path)
    if resolved_path.is_dir():
        return DirectoryRuntime(resolved_path, mode)
    if resolved_path.exists():
        return ZipArchive(resolved_path, mode)
    if resolved_path.suffix.lower() in {".ssp", ".fmu"}:
        return ZipArchive(resolved_path, mode)
    return DirectoryRuntime(resolved_path, mode)
