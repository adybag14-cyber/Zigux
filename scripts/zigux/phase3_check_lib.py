#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PREFIX = "check-phase3-"

WRAPPER_STUB = """#!/usr/bin/env python3
from __future__ import annotations

from phase3_check_lib import run_from_wrapper


if __name__ == \"__main__\":
    raise SystemExit(run_from_wrapper(__file__))
"""

SUPPORTED_SLUGS = {
    "abi": [sys.executable, "scripts/zigux/check-phase3-abi.py"],
}


def render_wrapper_stub() -> str:
    return WRAPPER_STUB


def slug_from_wrapper_path(path: str | Path) -> str:
    name = Path(path).name
    if not name.startswith(SCRIPT_PREFIX) or not name.endswith(".py"):
        raise SystemExit(f"unsupported Phase 3 wrapper path: {path}")
    return name[len(SCRIPT_PREFIX) : -3]


def shared_runner_gate_for_slug(slug: str) -> str:
    return f"PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug {slug}"


def run_phase3_check(slug: str, description: str | None = None, build_step: str | None = None, argv: list[str] | None = None) -> int:
    if slug not in SUPPORTED_SLUGS:
        raise SystemExit(f"unsupported Phase 3 slug: {slug}")
    cmd = [*SUPPORTED_SLUGS[slug], *(argv or [])]
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        print(f"PHASE3_RUN_STATUS=fail:{slug}")
        return result.returncode
    print(f"PHASE3_RUN_STATUS=pass:{slug}")
    return 0


def run_from_wrapper(path: str | Path) -> int:
    return run_phase3_check(slug_from_wrapper_path(path))


def run_self_test() -> int:
    expected_wrapper = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "from phase3_check_lib import run_from_wrapper",
            "",
            "",
            'if __name__ == "__main__":',
            '    raise SystemExit(run_from_wrapper(__file__))',
            "",
        ]
    )
    assert render_wrapper_stub() == expected_wrapper
    assert slug_from_wrapper_path("/tmp/check-phase3-abi.py") == "abi"
    try:
        slug_from_wrapper_path("/tmp/phase3-abi.py")
    except SystemExit as exc:
        assert str(exc) == "unsupported Phase 3 wrapper path: /tmp/phase3-abi.py"
    else:
        raise AssertionError("expected invalid wrapper path failure")
    assert shared_runner_gate_for_slug("abi") == "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi"
    print("PHASE3_CHECK_LIB_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared Phase 3 parity helper library.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    raise SystemExit("phase3_check_lib.py is a shared helper; pass --self-test")


if __name__ == "__main__":
    raise SystemExit(main())
