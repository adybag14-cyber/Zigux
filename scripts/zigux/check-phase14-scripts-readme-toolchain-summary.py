#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=scripts_readme_toolchain_summary

Fail-closed checker for the Phase 14 scripts-root toolchain summary.

This guard keeps P14-L07 focused on the operational reminder surface: the
scripts README must name the returned `phase14-validate` gate, the staged Zig
toolchain selection chain, the dedicated skbuff and RCU guardrails, and the
shared study-only companions without implying that missing Phase 14 wrapper
targets or deep-core ownership have returned.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=scripts_readme_toolchain_summary"
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

REQUIRED_MARKERS = [
    "## Phase 14",
    "the current scripts-root shared smoke packet stays reviewable",
    "make -C zigux phase14-validate",
    "the readable `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)` chain in `zigux/Makefile`",
    "without implying that manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides are the default current rerun path",
    "scripts/zigux/check-phase14-shared-smoke-route.py",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py",
    "scripts/zigux/check-phase14-rcu-rollback-guardrail.py",
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md",
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
]

FORBIDDEN_MARKERS = [
    "make -C zigux phase14-smoke replays the shipped",
    "make -C zigux phase14-test replays the shipped",
    "make -C zigux phase14 replays the shipped",
    "Phase 14 bridge parity is complete",
    "deep-core ownership has moved to Zigux",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def check(root: Path) -> list[str]:
    path = root / SCRIPTS_README_PATH
    if not path.exists():
        return [f"missing_file:{SCRIPTS_README_PATH.as_posix()}"]

    errors: list[str] = []
    text = read_text(root, SCRIPTS_README_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"missing_marker:{SCRIPTS_README_PATH.as_posix()}:{marker}")

    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            errors.append(f"forbidden_marker:{SCRIPTS_README_PATH.as_posix()}:{marker}")

    return errors


def fixture_readme() -> str:
    return """# scripts/zigux

## Phase 14

- Phase 14 flow - the current scripts-root shared smoke packet stays reviewable through `scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, and `scripts/zigux/validate-phase14.py` beside the returned `make -C zigux phase14-validate` gate.
- the readable `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)` chain in `zigux/Makefile` keeps the staged attached-toolchain path explicit without implying that manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides are the default current rerun path.
- `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`, `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, and `Documentation/zigux/phase15-study-only-anchor-accounting.md` remain explicit companions while missing broader wrapper targets stay historical vocabulary.
"""


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_text(root, SCRIPTS_README_PATH, fixture_readme())
        errors = check(root)
        if errors:
            raise AssertionError(f"expected fixture to pass, got {errors}")

        broken = fixture_readme().replace("scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py", "")
        write_text(root, SCRIPTS_README_PATH, broken)
        errors = check(root)
        if not any("check-phase14-skbuff-stay-in-c-guardrail.py" in error for error in errors):
            raise AssertionError("expected missing skbuff guard marker to fail")

        broken = fixture_readme() + "\nmake -C zigux phase14-smoke replays the shipped route\n"
        write_text(root, SCRIPTS_README_PATH, broken)
        errors = check(root)
        if not any("phase14-smoke" in error for error in errors):
            raise AssertionError("expected promoted phase14-smoke wording to fail")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in fixture checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print(f"{MARKER}_SELF_TEST=passed")
        return 0

    errors = check(Path(args.root))
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"{MARKER}=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
