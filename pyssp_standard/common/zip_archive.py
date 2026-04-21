from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import zipfile


class DirectoryFacade:
    """Shared directory-layer helper for unpacked SSP/FMU contents."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._root: Path | None = None

    def __enter__(self) -> "DirectoryFacade":
        if self.mode not in {"r", "a", "w"}:
            raise ValueError(f"Unsupported archive mode '{self.mode}'")

        if self.mode == "r":
            if not self.path.is_dir():
                raise FileNotFoundError(f"Directory does not exist: {self.path}")
        elif self.mode == "a":
            if self.path.exists() and not self.path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {self.path}")
            self.path.mkdir(parents=True, exist_ok=True)
        else:
            if self.path.exists() and not self.path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {self.path}")
            self.path.mkdir(parents=True, exist_ok=True)
            for entry in self.path.iterdir():
                if entry.is_dir():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()

        self._root = self.path
        return self

    def __exit__(self, exc_type, exc, tb):
        self._root = None
        return False

    @property
    def root(self) -> Path:
        if self._root is None:
            raise RuntimeError("Archive is not open")
        return self._root

    def namelist(self) -> list[str]:
        names: list[str] = []
        for entry in sorted(self.root.rglob("*")):
            if entry.is_file():
                names.append(entry.relative_to(self.root).as_posix())
        return names

    def read_text(self, name: str, encoding: str = "utf-8") -> str:
        return (self.root / name).read_text(encoding=encoding)

    def add_file(self, source: str | Path, target_name: str | None = None) -> str:
        source_path = Path(source)
        archive_name = target_name or source_path.name
        target_path = self.root / archive_name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        return archive_name

    def remove_file(self, target_name: str) -> None:
        target_path = self.root / target_name
        if target_path.exists():
            target_path.unlink()

    def list_prefix(self, prefix: str) -> list[str]:
        return [name for name in self.namelist() if name.startswith(prefix) and not name.endswith("/")]


class ZipArchiveFacade:
    """Shared archive-layer helper for .ssp and .fmu zip containers."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None
        self._directory = DirectoryFacade(self.path, mode)

    def __enter__(self) -> "ZipArchiveFacade":
        if self.mode not in {"r", "a", "w"}:
            raise ValueError(f"Unsupported archive mode '{self.mode}'")

        if self.mode == "r" and not self.path.exists():
            raise FileNotFoundError(f"Archive does not exist: {self.path}")

        self._temp_dir = tempfile.TemporaryDirectory(prefix=f"{self.path.stem}_archive_")
        self._directory = DirectoryFacade(self._temp_dir.name, mode="a")
        self._directory.__enter__()

        if self.mode in {"r", "a"} and self.path.exists() and self.path.stat().st_size > 0:
            with zipfile.ZipFile(self.path, "r") as archive:
                archive.extractall(self.root)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None and self.mode in {"w", "a"}:
                self._commit()
            return False
        finally:
            self._directory.__exit__(exc_type, exc, tb)
            if self._temp_dir is not None:
                self._temp_dir.cleanup()
                self._temp_dir = None

    @property
    def root(self) -> Path:
        return self._directory.root

    def namelist(self) -> list[str]:
        return self._directory.namelist()

    def read_text(self, name: str, encoding: str = "utf-8") -> str:
        return self._directory.read_text(name, encoding=encoding)

    def add_file(self, source: str | Path, target_name: str | None = None) -> str:
        return self._directory.add_file(source, target_name=target_name)

    def remove_file(self, target_name: str) -> None:
        self._directory.remove_file(target_name)

    def list_prefix(self, prefix: str) -> list[str]:
        return self._directory.list_prefix(prefix)

    def _commit(self) -> None:
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for entry in sorted(self.root.rglob("*")):
                if entry.is_file():
                    archive.write(entry, arcname=entry.relative_to(self.root).as_posix())


def open_archive(path: str | Path, mode: str = "r") -> DirectoryFacade | ZipArchiveFacade:
    resolved_path = Path(path)
    if resolved_path.is_dir():
        return DirectoryFacade(resolved_path, mode)
    if resolved_path.exists():
        return ZipArchiveFacade(resolved_path, mode)
    if resolved_path.suffix.lower() in {".ssp", ".fmu"}:
        return ZipArchiveFacade(resolved_path, mode)
    return DirectoryFacade(resolved_path, mode)
