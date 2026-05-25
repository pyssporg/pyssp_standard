from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pyssp_standard.md import ModelDescription
from pyssp_standard.common.archive_runtime import create_runtime
from pyssp_standard.ssp import SSP


class FMU:
    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self.runtime = create_runtime(self.path, mode)
        self._model_description: "ModelDescription" | None = None

    def __enter__(self) -> "FMU":
        self.runtime.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.runtime.__exit__(exc_type, exc, tb)
        return False

    @property
    def binaries(self) -> list[str]:
        return self.runtime.list_prefix("binaries/")

    @property
    def documentation(self) -> list[str]:
        return self.runtime.list_prefix("documentation/")

    @property
    def model_description(self) -> ModelDescription:
        return ModelDescription(self.runtime.root / "modelDescription.xml", mode=self.mode)

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the modelDescription.xml document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        with ModelDescription(self.runtime.root / "modelDescription.xml", mode=self.mode) as md:
            md.set_generation_date_and_time(dt)

    def package_as_ssp(
        self,
        path: str | Path,
        *,
        system_name: str | None = None,
        component_name: str | None = None,
        resource_name: str | None = None,
        implementation: str | None = None,
        expose_system_connectors: bool = False,
    ) -> Path:
        path = Path(path)
        component_name = component_name or self.path.stem
        system_name = system_name or path.stem

        with self.model_description as md:
            resolved_implementation = implementation or md.xml.interface_type or "ModelExchange"

        with SSP(path, mode="w") as ssp:
            ssp.add_fmu(
                component_name=component_name,
                fmu_path=self.path,
                resource_name=resource_name,
                implementation=resolved_implementation,
                expose_system_connectors=expose_system_connectors,
            )
            with ssp.system_structure() as ssd:
                ssd.xml.name = system_name
                if ssd.xml.system is not None:
                    ssd.xml.system.name = system_name

        return path
