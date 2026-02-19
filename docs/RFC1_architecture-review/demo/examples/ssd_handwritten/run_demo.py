from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples.ssd_handwritten.public_ssd_api import PublicSSD


file_path = ROOT / "data" / "example.ssd"

ssd = PublicSSD(file_path, mode="a")
print("Loaded SSD:", ssd.document.name, ssd.document.version)
print("Initial components:", len(ssd.document.components))
print("Initial connections:", len(ssd.document.connections))

if not any(c.name == "Controller" for c in ssd.document.components):
    ssd.add_component("Controller", "resources/controller.fmu")

if not any(
    c.start_element == "Controller"
    and c.start_connector == "y"
    and c.end_element == "Plant"
    and c.end_connector == "u"
    for c in ssd.document.connections
):
    ssd.connect("Controller", "y", "Plant", "u")

for diag in ssd.validate():
    print(f"[{diag.level}] {diag.message}")

ssd.save()

reloaded = PublicSSD(file_path, mode="r")
print("After save components:", len(reloaded.document.components))
print("After save connections:", len(reloaded.document.connections))
print("Saved file:", file_path)
