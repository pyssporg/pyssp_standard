from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
SCHEMA_PATH = HERE / "SystemStructureParameterValues.xsd"
OUTPUT_PATH = HERE / "ssv2_generated_types.py"


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


def generate_bindings(
    schema_path: Path = SCHEMA_PATH,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    schema_path = schema_path.resolve()
    output_path = output_path.resolve()

    xsdata_bin = resolve_xsdata_bin()
    env = os.environ.copy()
    env["PATH"] = f"{xsdata_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    with tempfile.TemporaryDirectory(prefix="xsdata_demo_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        subprocess.run(
            [
                str(xsdata_bin),
                "generate",
                str(schema_path),
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

        shutil.copyfile(generated_file, output_path)

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate demo xsdata bindings from XSD.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=SCHEMA_PATH,
        help="Path to the SSV schema root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Path to the checked-in generated python module.",
    )
    args = parser.parse_args()
    output = generate_bindings(schema_path=args.schema, output_path=args.output)
    print(output)


if __name__ == "__main__":
    main()
