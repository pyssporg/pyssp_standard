from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.operations.model_description_to_ssd import create_component_from_model_description
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1System
from pyssp_standard.standard.ssp1.operations.model_description_to_ssd import add_component_to_system_structure
from pyssp_standard.ssd import ParameterBinding, SsdRuntime
from pyssp_standard.common.archive_runtime import DirectoryRuntime, create_runtime, ArchiveRuntime


class SSP:
    def __init__(self, path: str | Path, mode: str = "a"):
        self.path = Path(path)
        self.mode = mode
        self._runtime : DirectoryRuntime | ArchiveRuntime = create_runtime(self.path, mode)

    def __enter__(self) -> "SSP":
        self._runtime.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            return self._runtime.__exit__(exc_type, exc, tb)
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

    def add_external_parameterset(
        self,
        parameter_set_path: str | Path,
        mapping_path: str | Path | None = None,
        *,
        resource_name: str | None = None,
        mapping_resource_name: str | None = None,
        prefix: str | None = None,
    ) -> ParameterBinding:
        parameter_set_path = Path(parameter_set_path)
        parameter_set_resource_name = (
            self.add_resource(parameter_set_path)
            if resource_name is None
            else self.runtime.add_file(parameter_set_path, target_name=f"resources/{resource_name}").removeprefix("resources/")
        )

        mapping_resource_name = (
            None
            if mapping_path is None
            else (
                self.add_resource(mapping_path)
                if mapping_resource_name is None
                else self.runtime.add_file(
                    Path(mapping_path),
                    target_name=f"resources/{mapping_resource_name}",
                ).removeprefix("resources/")
            )
        )

        with self.system_structure() as ssd:
            if ssd.xml.system is None:
                ssd.xml.system = Ssd1System(name=ssd.xml.name or "system")
            return ssd.xml.system.add_external_parameterset(
                source=f"resources/{parameter_set_resource_name}",
                mapping_source=(
                    f"resources/{mapping_resource_name}" if mapping_resource_name is not None else None
                ),
                prefix=prefix,
            )

    def remove_resource(self, resource_name: str) -> None:
        self.runtime.remove_file(f"resources/{resource_name}")

    def system_structure(self, path="SystemStructure.ssd" ) -> SsdRuntime:
        return SsdRuntime(self.runtime, ssd_path=path, mode="a" if self.mode == "w" else self.mode)

    def add_fmu(
        self,
        component_name: str,
        fmu_path: str | Path,
        *,
        resource_name: str | None = None,
        implementation: str | None = "ModelExchange",
        component_type: str | None = "application/x-fmu-sharedlibrary",
        expose_system_connectors: bool = False,
        connector_prefix: str | None = None,
    ) -> str:
        from pyssp_standard.fmu import FMU

        fmu_path = Path(fmu_path)
        added_resource_name = (
            self.add_resource(fmu_path)
            if resource_name is None
            else self.runtime.add_file(fmu_path, target_name=f"resources/{resource_name}").removeprefix("resources/")
        )

        with FMU(fmu_path, mode="r") as fmu:
            with fmu.model_description as md:
                component = create_component_from_model_description(
                    md.xml,
                    component_name=component_name,
                    source=f"resources/{added_resource_name}",
                    implementation=implementation,
                    component_type=component_type,
                )

        with self.system_structure() as ssd:
            add_component_to_system_structure(
                ssd.xml,
                component,
                expose_system_connectors=expose_system_connectors,
                connector_prefix=connector_prefix,
                default_system_name=self.path.stem or "system",
            )

        return added_resource_name
