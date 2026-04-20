from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pyssp_standard.tools.xsdata_generation import TARGETS, generate_targets


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate versioned xsdata binding modules for pyssp_standard internals."
    )
    parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        choices=sorted(TARGETS.keys()),
        help="Generation target key. Repeat to generate multiple targets. Defaults to all targets.",
    )
    args = parser.parse_args()

    targets = args.targets or sorted(TARGETS.keys())
    outputs = generate_targets(targets)
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
