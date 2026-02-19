from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples.ssd_binding_modes.public_api import PublicSSD


def run_case(case_file: Path):
    ssd = PublicSSD(case_file, mode="a")
    print(f"\n--- {case_file.name} ---")
    print("Loaded SSD:", ssd.document.name, ssd.document.version)
    print("Components:", len(ssd.document.components))
    print("Bindings:", [(b.target, b.mode) for b in ssd.document.parameter_bindings])

    # Add one idempotent parameter to show editable authoring API behavior
    if any(b.mode == "inline" for b in ssd.document.parameter_bindings):
        ssd.add_parameter(target="Plant", mode="inline", name="offset", value=2.0)
    if any(b.mode == "external" for b in ssd.document.parameter_bindings):
        ssd.add_parameter(
            target="Plant",
            mode="external",
            name="offset",
            value=2.0,
            external_path="external_values.ssv",
        )

    for diag in ssd.validate():
        print(f"[{diag.level}] {diag.message}")

    ssd.save()

    reloaded = PublicSSD(case_file, mode="r")
    print("After save bindings:", [(b.target, b.mode) for b in reloaded.document.parameter_bindings])


run_case(ROOT / "data" / "inline_example.ssd")
run_case(ROOT / "data" / "external_example.ssd")
print("Updated files in:", ROOT / "data")
