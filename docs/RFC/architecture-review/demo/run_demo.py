from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

from demo.public_api import PublicSSP, PublicSSV


def run_case(case_file: Path, *, codec_name: str):
    ssp = PublicSSP(ROOT, ssv_codec_name=codec_name)
    public_ssv = PublicSSV(codec_name=codec_name)
    ssd = ssp.load_ssd(Path("__data__") / case_file.name)
    print(f"\n--- {case_file.name} [{codec_name}] ---")
    print("Loaded SSD:", ssd.name, ssd.version)
    print("Components:", len(ssd.components))
    print(
        "Bindings:", [(b.target, b.is_inlined, b.is_resolved) for b in ssd.parameter_bindings]
    )

    # Add one idempotent parameter to show editable authoring API behavior
    for binding in ssd.parameter_bindings:
        if binding.parameter_set is None:
            continue
        public_ssv.add_parameter(binding.parameter_set, name="offset", value=2.0)

    new_name = case_file.stem + case_file.suffix
    ssp.save_ssd(Path("__data__") / "result" / new_name, ssd)

    reloaded = ssp.load_ssd(Path("__data__") / "result" / new_name)
    print(
        "After save bindings:",
        [(b.target, b.is_inlined, b.is_resolved) for b in reloaded.parameter_bindings],
    )


run_case(ROOT / "__data__" / "mixed_example.ssd", codec_name="xsdata")
print("Updated files in:", ROOT / "__data__")
