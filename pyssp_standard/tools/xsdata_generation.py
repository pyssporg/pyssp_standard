from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class BindingTarget:
    name: str
    family: str
    version: str
    schema_path: Path
    output_path: Path


TARGETS: dict[str, BindingTarget] = {
    "ssp1_ssv": BindingTarget(
        name="ssp1_ssv",
        family="SSP",
        version="1.0",
        schema_path=REPO_ROOT / "3rdParty" / "SSP1" / "schema" / "SystemStructureParameterValues.xsd",
        output_path=REPO_ROOT / "pyssp_standard" / "standard" / "ssp1" / "generated" / "ssv_generated_types.py",
    ),
    "ssp1_ssd": BindingTarget(
        name="ssp1_ssd",
        family="SSP",
        version="1.0",
        schema_path=REPO_ROOT / "3rdParty" / "SSP1" / "schema" / "SystemStructureDescription.xsd",
        output_path=REPO_ROOT / "pyssp_standard" / "standard" / "ssp1" / "generated" / "ssd_generated_types.py",
    ),
    "ssp1_ssm": BindingTarget(
        name="ssp1_ssm",
        family="SSP",
        version="1.0",
        schema_path=REPO_ROOT / "3rdParty" / "SSP1" / "schema" / "SystemStructureParameterMapping.xsd",
        output_path=REPO_ROOT / "pyssp_standard" / "standard" / "ssp1" / "generated" / "ssm_generated_types.py",
    ),
    "ssp2_ssv": BindingTarget(
        name="ssp2_ssv",
        family="SSP",
        version="2.0",
        schema_path=REPO_ROOT / "3rdParty" / "SSP2" / "schema" / "SystemStructureParameterValues.xsd",
        output_path=REPO_ROOT / "pyssp_standard" / "standard" / "ssp2" / "generated" / "ssv_generated_types.py",
    ),
    "fmi2_model_description": BindingTarget(
        name="fmi2_model_description",
        family="FMI",
        version="2.0",
        schema_path=REPO_ROOT / "3rdParty" / "FMI2" / "schema" / "fmi2ModelDescription.xsd",
        output_path=REPO_ROOT / "pyssp_standard" / "standard" / "fmi2" / "generated" / "model_description_generated_types.py",
    ),
}


def resolve_xsdata_bin() -> Path:
    candidates = [
        REPO_ROOT / "venv" / "bin" / "xsdata",
        Path(sys.executable).resolve().parent / "xsdata",
    ]
    which = shutil.which("xsdata")
    if which:
        candidates.append(Path(which))

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("Could not locate an xsdata executable")


def generate_target(target: BindingTarget) -> Path:
    xsdata_bin = resolve_xsdata_bin()
    env = os.environ.copy()
    env["PATH"] = f"{xsdata_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    target.output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"xsdata_{target.name}_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        subprocess.run(
            [
                str(xsdata_bin),
                "generate",
                str(target.schema_path),
                "-p",
                "bindings",
                "-ss",
                "single-package",
                "--relative-imports",
            ],
            cwd=tmp_path,
            env=env,
            check=True,
        )
        generated_file = tmp_path / "bindings.py"
        if not generated_file.exists():
            raise FileNotFoundError(f"xsdata did not produce expected file: {generated_file}")

        shutil.copyfile(generated_file, target.output_path)

    return target.output_path


def generate_targets(target_names: list[str]) -> list[Path]:
    outputs: list[Path] = []
    for name in target_names:
        if name not in TARGETS:
            raise KeyError(f"Unknown generation target: {name}")
        outputs.append(generate_target(TARGETS[name]))
    return outputs
