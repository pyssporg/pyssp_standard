from __future__ import annotations

from pathlib import Path

from pyssp_standard.archive import ZipArchiveFacade


class SSP:
    def __init__(self, path: str | Path, mode: str = "a"):
        self.path = Path(path)
        self.mode = mode
        self._archive = ZipArchiveFacade(self.path, mode)

    def __enter__(self) -> "SSP":
        self._archive.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._archive.__exit__(exc_type, exc, tb)
        return False

    @property
    def resources(self) -> list[str]:
        return [name.removeprefix("resources/") for name in self._archive.list_prefix("resources/")]

    def add_resource(self, source: str | Path) -> str:
        source_path = Path(source)
        return self._archive.add_file(source_path, target_name=f"resources/{source_path.name}").removeprefix("resources/")

    def remove_resource(self, resource_name: str) -> None:
        self._archive.remove_file(f"resources/{resource_name}")

    @property
    def system_structure(self) -> Path:
        # TODO: return  tmp "systemstructure.xml" path to be used with a context 
        pass