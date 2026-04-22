from __future__ import annotations

from pathlib import Path

from pyssp_standard.ssd import SsdRuntime
from pyssp_standard.common.zip_archive import DirectoryRuntime, open_archive


class SSP:
    def __init__(self, path: str | Path, mode: str = "a"):
        self.path = Path(path)
        self.mode = mode
        self._archive = open_archive(self.path, mode)
        self._runtime: DirectoryRuntime | None = None

    def __enter__(self) -> "SSP":
        self._runtime = self._archive.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            return self._archive.__exit__(exc_type, exc, tb)
        finally:
            self._runtime = None

    @property
    def runtime(self) -> DirectoryRuntime:
        if self._runtime is None:
            raise RuntimeError("SSP is not open")
        return self._runtime

    @property
    def resources(self) -> list[str]:
        return [name.removeprefix("resources/") for name in self.runtime.list_prefix("resources/")]

    def add_resource(self, source: str | Path) -> str:
        source_path = Path(source)
        return self.runtime.add_file(source_path, target_name=f"resources/{source_path.name}").removeprefix("resources/")

    def remove_resource(self, resource_name: str) -> None:
        self.runtime.remove_file(f"resources/{resource_name}")

    def system_structure(self, path="SystemStructure.ssd" ) -> SsdRuntime:
        return SsdRuntime(self.runtime, ssd_path=path, mode="a" if self.mode == "w" else self.mode)
