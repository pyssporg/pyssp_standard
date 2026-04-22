from __future__ import annotations

from pathlib import Path
import shutil


class DirectoryRuntime:
    """Shared directory-layer helper for unpacked SSP/FMU contents."""

    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._root: Path | None = None

    def __enter__(self) -> "DirectoryRuntime":
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

    def resolve(self, path: str | Path) -> Path:
        return self.root / Path(path)

    def namelist(self) -> list[str]:
        names: list[str] = []
        for entry in sorted(self.root.rglob("*")):
            if entry.is_file():
                names.append(entry.relative_to(self.root).as_posix())
        return names

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        return self.resolve(path).read_text(encoding=encoding)

    def add_file(self, source: str | Path, target_name: str | None = None) -> str:
        source_path = Path(source)
        archive_name = target_name or source_path.name
        target_path = self.resolve(archive_name)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        return archive_name

    def remove_file(self, target_name: str) -> None:
        target_path = self.resolve(target_name)
        if target_path.exists():
            target_path.unlink()

    def list_prefix(self, prefix: str) -> list[str]:
        return [name for name in self.namelist() if name.startswith(prefix) and not name.endswith("/")]

