#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from phase3_check_lib import run_from_wrapper


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    syntax_check = subprocess.run(
        [sys.executable, "scripts/zigux/validate-phase3-abi-bindings-syntax.py"],
        cwd=ROOT,
        check=False,
    )
    if syntax_check.returncode != 0:
        return syntax_check.returncode
    return run_from_wrapper(__file__)


if __name__ == "__main__":
    raise SystemExit(main())
