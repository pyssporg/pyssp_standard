from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path

from pyssp_standard.standard.operations.model_description_to_ssd import (
    create_component_from_model_description,
)
from pyssp_standard.ls_ref import (
    LS_REF_EXTRA_DIR,
    LSRefExperiment,
    LSRefExperiments,
)
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1System
from pyssp_standard.standard.ssp1.operations.ssd_fmu_iteration import (
    FmuEntry,
    iter_fmu_entries,
)
from pyssp_standard.standard.ssp1.operations.model_description_to_ssd import (
    add_component_to_system_structure,
)
from pyssp_standard.ssd import ParameterBinding, SSD
from pyssp_standard.common.document_runtime import DocumentRuntime
from pyssp_standard.common.reference_specs import EXTERNAL_REFERENCE_SPECS
from pyssp_standard.common.archive import copy_resource_directory
from pyssp_standard.common.archive_runtime import (
    DirectoryRuntime,
    create_runtime,
    ArchiveRuntime,
)


class SSP:
    def __init__(self, path: str | Path, mode: str = "a"):
        self.path = Path(path)
        self.mode = mode
        self._runtime: DirectoryRuntime | ArchiveRuntime = create_runtime(
            self.path, mode
        )

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
        return [
            name.removeprefix("resources/")
            for name in self.runtime.list_prefix("resources/")
        ]

    def add_resource(self, source: str | Path) -> str:
        source_path = Path(source)
        return self.runtime.add_file(
            source_path, target_name=f"resources/{source_path.name}"
        ).removeprefix("resources/")

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
            else self.runtime.add_file(
                parameter_set_path, target_name=f"resources/{resource_name}"
            ).removeprefix("resources/")
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
                    f"resources/{mapping_resource_name}"
                    if mapping_resource_name is not None
                    else None
                ),
                prefix=prefix,
            )

    def remove_resource(self, resource_name: str) -> None:
        self.runtime.remove_file(f"resources/{resource_name}")

    def system_structure(self, path="SystemStructure.ssd") -> DocumentRuntime[SSD]:
        return DocumentRuntime[SSD](
            self.runtime,
            document_path=path,
            document_type=SSD,
            external_reference_specs=EXTERNAL_REFERENCE_SPECS,
            mode="a" if self.mode == "w" else self.mode,
        )

    def iter_fmu_entries(
        self,
        *,
        recursive: bool = False,
        skip_missing: bool = True,
    ) -> Iterator[FmuEntry]:
        """Yield ``FmuEntry`` for every component whose source references an FMU resource.

        Opens the ``SystemStructure.ssd`` document lazily and delegates to
        :func:`~pyssp_standard.standard.ssp1.operations.ssd_fmu_iteration.iter_fmu_entries`,
        yielding entries as they are discovered.

        Args:
            recursive: If True, recurse into nested ``Ssd1System`` subsystems.
            skip_missing: If True, skip components whose resolved source path
                does not exist on disk.

        Yields:
            :class:`~pyssp_standard.standard.ssp1.operations.ssd_fmu_iteration.FmuEntry`
            instances for each FMU-backed component.
        """
        with self.system_structure() as ssd:
            if ssd.xml.system is None:
                return
            yield from iter_fmu_entries(
                ssd.xml.system,
                self.runtime,
                recursive=recursive,
                skip_missing=skip_missing,
            )

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the SystemStructure.ssd document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        with self.system_structure() as ssd:
            ssd.set_generation_date_and_time(dt)

    def ls_ref_experiments(
        self, path=f"{LS_REF_EXTRA_DIR}/experiments.xml"
    ) -> DocumentRuntime[LSRefExperiments]:
        return DocumentRuntime[LSRefExperiments](
            self.runtime,
            document_path=path,
            document_type=LSRefExperiments,
            mode="a" if self.mode == "w" else self.mode,
        )

    def add_ls_ref_experiment(
        self, experiments: LSRefExperiment | Iterable[LSRefExperiment]
    ) -> str:
        with self.ls_ref_experiments() as ref:
            ref.add_experiment(experiments)

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
        """Add an FMU to the SSP archive and create an SSD component.

        *fmu_path* may be a ``.fmu`` archive file or an extracted FMU directory.
        When a directory is provided, its contents are copied recursively under
        ``resources/`` and ``modelDescription.xml`` must exist inside it.

        Args:
            component_name: Name for the component in the SSD.
            fmu_path: Path to a ``.fmu`` file or an extracted FMU directory.
            resource_name: Optional explicit resource name. When *fmu_path* is a
                directory and *resource_name* is ``None``, the directory basename
                is used as the resource name.
            implementation: FMI implementation type (default ``"ModelExchange"``).
            component_type: Component type MIME (default
                ``"application/x-fmu-sharedlibrary"``).
            expose_system_connectors: If ``True``, mirror component connectors
                to the system level.
            connector_prefix: Optional prefix for system-level connectors.

        Returns:
            The resource name under ``resources/`` (e.g. ``"0001_ECS_HW.fmu"``).

        Raises:
            FileNotFoundError: If *fmu_path* does not exist, or if a directory
                *fmu_path* does not contain ``modelDescription.xml``.
            FileExistsError: If *fmu_path* is a directory and the target
                resource path already exists (via ``copy_resource_directory``).
        """
        from pyssp_standard.fmu import FMU

        fmu_path = Path(fmu_path)

        # Branch: directory FMU vs file FMU
        if fmu_path.is_dir():
            # Validate modelDescription.xml exists inside the directory
            model_desc_path = fmu_path / "modelDescription.xml"
            if not model_desc_path.is_file():
                raise FileNotFoundError(
                    f"FMU directory does not contain modelDescription.xml: {model_desc_path}"
                )

            target_resource_name = resource_name or fmu_path.name
            if Path(target_resource_name).suffix.lower() != ".fmu":
                target_resource_name = f"{target_resource_name}.fmu"
            added_resource_name = copy_resource_directory(
                fmu_path, self.runtime.resolve("resources"), target_resource_name
            )
        else:
            added_resource_name = (
                self.add_resource(fmu_path)
                if resource_name is None
                else self.runtime.add_file(
                    fmu_path, target_name=f"resources/{resource_name}"
                ).removeprefix("resources/")
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
