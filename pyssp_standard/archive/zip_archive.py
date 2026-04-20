from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import zipfile


class ZipArchiveFacade:
    """Shared archive-layer helper for .ssp and .fmu zip containers."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None
        self._workdir: Path | None = None

    def __enter__(self) -> "ZipArchiveFacade":
        if self.mode not in {"r", "a", "w"}:
            raise ValueError(f"Unsupported archive mode '{self.mode}'")

        self._temp_dir = tempfile.TemporaryDirectory(prefix=f"{self.path.stem}_archive_")
        self._workdir = Path(self._temp_dir.name)

        if self.mode in {"r", "a"} and self.path.exists() and self.path.stat().st_size > 0:
            with zipfile.ZipFile(self.path, "r") as archive:
                archive.extractall(self._workdir)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None and self.mode in {"w", "a"}:
            self._commit()
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None
            self._workdir = None
        return False

    def namelist(self) -> list[str]:
        workdir = self._require_workdir()
        names: list[str] = []
        for entry in sorted(workdir.rglob("*")):
            if entry.is_file():
                names.append(entry.relative_to(workdir).as_posix())
        return names

    def read_text(self, name: str, encoding: str = "utf-8") -> str:
        target = self._require_workdir() / name
        return target.read_text(encoding=encoding)

    def add_file(self, source: str | Path, target_name: str | None = None) -> str:
        source_path = Path(source)
        archive_name = target_name or source_path.name
        target_path = self._require_workdir() / archive_name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        return archive_name

    def remove_file(self, target_name: str) -> None:
        target_path = self._require_workdir() / target_name
        if target_path.exists():
            target_path.unlink()

    def list_prefix(self, prefix: str) -> list[str]:
        return [name for name in self.namelist() if name.startswith(prefix) and not name.endswith("/")]

    def _commit(self) -> None:
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            workdir = self._require_workdir()
            for entry in sorted(workdir.rglob("*")):
                if entry.is_file():
                    archive.write(entry, arcname=entry.relative_to(workdir).as_posix())

    def _require_workdir(self) -> Path:
        if self._workdir is None:
            raise RuntimeError("Archive is not open")
        return self._workdir
