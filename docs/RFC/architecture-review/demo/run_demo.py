from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples.ssd_binding_modes.public_api import PublicSSP


def run_case(case_file: Path):
    ssp = PublicSSP(ROOT)
    ssd = ssp.load_ssd(Path("data") / case_file.name)
    print(f"\n--- {case_file.name} ---")
    print("Loaded SSD:", ssd.name, ssd.version)
    print("Components:", len(ssd.components))
    print(
        "Bindings:", [(b.target, b.mode, b.is_resolved) for b in ssd.parameter_bindings]
    )

    # Add one idempotent parameter to show editable authoring API behavior
    for binding in ssd.parameter_bindings:
        if binding.parameter_set is None:
            continue
        if not any(p.name == "offset" for p in binding.parameter_set.parameters):
            binding.parameter_set.add_real_parameter("offset", 2.0)

    ssp.save_ssd(Path("data") / case_file.name + "new", ssd)

    reloaded = ssp.load_ssd(Path("data") / case_file.name + "new")
    print(
        "After save bindings:",
        [(b.target, b.mode, b.is_resolved) for b in reloaded.parameter_bindings],
    )


run_case(ROOT / "data" / "mixed_example.ssd")
print("Updated files in:", ROOT / "data")
