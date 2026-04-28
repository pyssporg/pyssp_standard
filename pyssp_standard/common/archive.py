from __future__ import annotations

import shutil
import stat
import tempfile
import zipfile
from pathlib import Path


EXECUTABLE_PERMISSION_BITS = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
UNIX_PERMISSION_SHIFT = 16


def _is_library_path(path: str | Path) -> bool:
    return "binaries" in Path(path).parts


def _with_executable_bits(file_mode: int) -> int:
    return file_mode | EXECUTABLE_PERMISSION_BITS


def _zip_external_attr(file_mode: int) -> int:
    return (file_mode & 0xFFFF) << UNIX_PERMISSION_SHIFT


def _chmod_library_files(root_dir: Path) -> None:
    for path in root_dir.rglob("*"):
        if path.is_file() and _is_library_path(path.relative_to(root_dir)):
            path.chmod(_with_executable_bits(path.stat().st_mode))


def _write_archive_file(archive: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo.from_file(path, arcname=arcname)
    info.compress_type = zipfile.ZIP_DEFLATED
    if _is_library_path(arcname):
        info.external_attr = _zip_external_attr(_with_executable_bits(path.stat().st_mode))

    with path.open("rb") as source:
        archive.writestr(info, source.read())


def default_output_dir(archive_path: str | Path) -> Path:
    archive = Path(archive_path)
    return archive.parent / archive.stem

def unpack_archive(
    archive_path: str | Path,
    output_dir: str | Path | None = None,
    *,
    recursive_fmus: bool = False,
    overwrite: bool = False,
) -> Path:
    archive_path = Path(archive_path)
    suffix = archive_path.suffix.lower()
    if suffix not in {".fmu", ".ssp"}:
        raise ValueError(f"Expected a .fmu or .ssp archive, got: {archive_path.name}")

    output_dir = Path(output_dir) if output_dir is not None else default_output_dir(archive_path)
    if output_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Output path already exists: {output_dir}")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(output_dir)
    _chmod_library_files(output_dir)

    if suffix == ".fmu":
        return output_dir

    if not recursive_fmus:
        return output_dir

    for fmu_archive in sorted(output_dir.rglob("*.fmu")):
        if not fmu_archive.is_file():
            continue

        # Unpack to temp dir and then move if there are errors while unpacking
        unpack_dir = fmu_archive.with_suffix("")
        temp_unpack_dir = fmu_archive.parent / f"{fmu_archive.name}.tmp-unpack"
        temp_unpack_dir.mkdir(parents=True, exist_ok=False)
        with zipfile.ZipFile(fmu_archive, "r") as archive:
            archive.extractall(temp_unpack_dir)
        _chmod_library_files(temp_unpack_dir)
        fmu_archive.unlink()
        temp_unpack_dir.rename(unpack_dir)

    return output_dir


def package_archive(
    source_dir: str | Path,
    archive_path: str | Path,
    *,
    nested_fmus: bool = False,
    overwrite: bool = True,
) -> Path:
    source_dir = Path(source_dir)
    archive_path = Path(archive_path)
    suffix = archive_path.suffix.lower()
    if suffix not in {".fmu", ".ssp"}:
        raise ValueError(f"Expected a .fmu or .ssp output archive, got: {archive_path.name}")
    
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if archive_path.exists():
        if not overwrite:
            raise FileExistsError(f"Archive already exists: {archive_path}")
        archive_path.unlink()
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    archive_root = source_dir
    temp_dir: tempfile.TemporaryDirectory[str] | None = None

    if suffix == ".ssp" and nested_fmus:
        temp_dir = tempfile.TemporaryDirectory(prefix=f"{archive_path.stem}_package_")
        
        archive_root = Path(temp_dir.name) / source_dir.name
        shutil.copytree(source_dir, archive_root)

        resources_dir = archive_root / "resources"
        if resources_dir.is_dir():
            for candidate in sorted(resources_dir.iterdir()):
                if not candidate.is_dir():
                    continue
                if not (candidate / "modelDescription.xml").is_file():
                    continue
                fmu_path = candidate.with_suffix(".fmu")
                with zipfile.ZipFile(fmu_path, "w", compression=zipfile.ZIP_DEFLATED) as fmu_archive:
                    for path in sorted(candidate.rglob("*")):
                        if path.is_file():
                            _write_archive_file(
                                fmu_archive,
                                path,
                                path.relative_to(candidate).as_posix(),
                            )
                shutil.rmtree(candidate)

    try:
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(archive_root.rglob("*")):
                if path.is_file():
                    _write_archive_file(
                        archive,
                        path,
                        path.relative_to(archive_root).as_posix(),
                    )
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    return archive_path
