#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from phase3_check_lib import run_from_wrapper


ROOT = Path(__file__).resolve().parents[2]
SYNTAX_CHECKER = ROOT / "scripts" / "zigux" / "validate-phase3-abi-bindings-syntax.py"


if __name__ == "__main__":
    syntax_result = subprocess.run([sys.executable, str(SYNTAX_CHECKER)], check=False)
    if syntax_result.returncode != 0:
        raise SystemExit(syntax_result.returncode)
    raise SystemExit(run_from_wrapper(__file__))
