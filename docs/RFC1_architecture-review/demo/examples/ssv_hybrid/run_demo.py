from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples.ssv_hybrid.public_ssv_api import PublicSSV


in_file = ROOT / "data" / "example.ssv"
out_file = ROOT / "data" / "example_out.ssv"

ssv = PublicSSV(in_file, mode="a")
print("Loaded version:", ssv.version)
print("Initial parameter count:", len(ssv.model.parameters))

for d in ssv.validate():
    print(f"[{d.level}] {d.message}")

if not any(p.name == "offset" for p in ssv.model.parameters):
    ssv.add_parameter("offset", 2.0)
ssv.save()

saved = PublicSSV(in_file, mode="r")
print("After save parameter count:", len(saved.model.parameters))
print("Saved file:", in_file)

# Demonstrate compatibility with explicit copy step in this mockup
out_file.write_text(in_file.read_text(encoding="utf-8"), encoding="utf-8")
print("Copied output file:", out_file)
