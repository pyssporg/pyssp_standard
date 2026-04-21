from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Ensure tests can import runtime dependencies installed in the repo venv.
VENV_SITE = REPO_ROOT / "venv" / "lib" / "python3.10" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
    sys.path.insert(0, str(VENV_SITE))


collect_ignore_glob = ["pytest/legacy_unsupported/test_*.py"]
