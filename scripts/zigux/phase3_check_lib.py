#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

from phase3_catalog import discover_phase3_slices

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PREFIX = "check-phase3-"

WRAPPER_STUB = """#!/usr/bin/env python3
from __future__ import annotations

from phase3_check_lib import run_from_wrapper


if __name__ == "__main__":
    raise SystemExit(run_from_wrapper(__file__))
"""


def render_wrapper_stub() -> str:
    return WRAPPER_STUB


def slug_from_wrapper_path(path: str | Path) -> str:
    name = Path(path).name
    if not name.startswith(SCRIPT_PREFIX) or not name.endswith(".py"):
        raise SystemExit(f"unsupported Phase 3 wrapper path: {path}")
    return name[len(SCRIPT_PREFIX) : -3]


def discovered_commands(root: Path = ROOT) -> dict[str, list[str]]:
    commands: dict[str, list[str]] = {}
    for entry in discover_phase3_slices(root):
        commands[entry.slug] = [
            sys.executable,
            entry.check_script.relative_to(root).as_posix(),
        ]
    return commands


def shared_runner_gate_for_slug(slug: str) -> str:
    return f"PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug {slug}"


def run_phase3_check(
    slug: str,
    description: str | None = None,
    build_step: str | None = None,
    argv: list[str] | None = None,
    root: Path = ROOT,
) -> int:
    commands = discovered_commands(root)
    if slug not in commands:
        raise SystemExit(f"unsupported Phase 3 slug: {slug}")
    cmd = [*commands[slug], *(argv or [])]
    result = subprocess.run(cmd, cwd=root, check=False)
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
            "    raise SystemExit(run_from_wrapper(__file__))",
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

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_check_lib_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        for rel in [
            "Documentation/zigux/phase3-abi-slice.md",
            "scripts/zigux/check-phase3-abi.py",
            "zigux/tests/phase3_abi_dump.zig",
            "zigux/tests/fixtures/phase3_abi/expected.json",
            "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
        ]:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# stub\n", encoding="utf-8")
        assert discovered_commands(root) == {
            "abi": [sys.executable, "scripts/zigux/check-phase3-abi.py"]
        }
        try:
            run_phase3_check("missing", root=root)
        except SystemExit as exc:
            assert str(exc) == "unsupported Phase 3 slug: missing"
        else:
            raise AssertionError("expected unsupported slug failure")
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
