from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1Component, Ssd1Connection, Ssd1Connector, Ssd1System
from pyssp_standard.ssd import SsdRuntime
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
        added_resource_name = self.add_resource(fmu_path) if resource_name is None else self.runtime.add_file(fmu_path, target_name=f"resources/{resource_name}").removeprefix("resources/")

        with FMU(fmu_path, mode="r") as fmu:
            with fmu.model_description as md:
                variables = list(md.xml.parameters) + list(md.xml.inputs) + list(md.xml.outputs)

        component = Ssd1Component(
            name=component_name,
            source=f"resources/{added_resource_name}",
            component_type=component_type,
            implementation=implementation,
        )
        component_connector_names: list[str] = []

        for variable in variables:
            connector = Ssd1Connector(
                name=variable.name,
                kind=variable.causality or "",
                type_name=variable.type_name,
                type_attributes=dict(variable.type_attributes),
            )
            if variable.declared_type is not None:
                connector.type_attributes["declaredType"] = variable.declared_type
            if variable.start is not None:
                connector.type_attributes["start"] = variable.start
            component.connectors.append(connector)
            component_connector_names.append(variable.name)

        with self.system_structure() as ssd:
            if ssd.xml.system is None:
                ssd.xml.system = Ssd1System(name=ssd.xml.name or self.path.stem or "system")
            ssd.xml.system.elements.append(component)

            if not expose_system_connectors:
                return added_resource_name

            for component_connector_name, component_connector in zip(component_connector_names, component.connectors):
                connector_name = f"{connector_prefix}{component_connector_name}" if connector_prefix else component_connector_name
                system_connector = Ssd1Connector(
                    name=connector_name,
                    kind=component_connector.kind,
                    type_name=component_connector.type_name,
                    type_attributes=dict(component_connector.type_attributes),
                )
                ssd.xml.system.connectors.append(system_connector)
                if component_connector.kind == "output":
                    ssd.xml.system.connections.append(
                        Ssd1Connection(
                            start_element=component_name,
                            start_connector=component_connector_name,
                            end_connector=connector_name,
                        )
                    )
                else:
                    ssd.xml.system.connections.append(
                        Ssd1Connection(
                            start_connector=connector_name,
                            end_element=component_name,
                            end_connector=component_connector_name,
                        )
                    )

        return added_resource_name
