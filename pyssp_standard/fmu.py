from __future__ import annotations

from pathlib import Path

from pyssp_standard.md import ModelDescription
from pyssp_standard.common.zip_archive import ZipArchiveFacade


class FMU:
    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._archive = ZipArchiveFacade(self.path, mode)
        self._model_description: "ModelDescription" | None = None

    def __enter__(self) -> "FMU":
        self._archive.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._archive.__exit__(exc_type, exc, tb)
        return False

    @property
    def binaries(self) -> list[str]:
        return self._archive.list_prefix("binaries/")

    @property
    def documentation(self) -> list[str]:
        return self._archive.list_prefix("documentation/")

    @property
    def model_description(self) -> ModelDescription:
        return ModelDescription(self._archive._require_workdir() / "modelDescription.xml")
