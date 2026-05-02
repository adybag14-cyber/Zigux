#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"


def main() -> int:
    if not CLOSURE_VALIDATOR.exists():
        print("PHASE2_VALIDATION=fail")
        print(
            "MISSING_PHASE2_CLOSURE_VALIDATOR="
            f"{CLOSURE_VALIDATOR.relative_to(ROOT)}"
        )
        return 1

    result = subprocess.run([sys.executable, str(CLOSURE_VALIDATOR)], cwd=ROOT)
    if result.returncode == 0:
        print("PHASE2_VALIDATION=pass")
    else:
        print("PHASE2_VALIDATION=fail")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
