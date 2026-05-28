#!/usr/bin/env python3
"""Guard the current Phase 2 scripts-root fixdep reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SCRIPTS_README = Path("scripts/zigux/README.md")
MAKEFILE = Path("zigux/Makefile")
FIXDEP_GATE = Path("scripts/zigux/check-phase2-fixdep-gate.py")
FIXDEP_DIFF = Path("scripts/zigux/check-fixdep-diff.py")
FIXDEP_ZIG = Path("scripts/zigux/fixdep.zig")
FIXDEP_CASES = Path("zigux/tests/fixtures/fixdep/cases.json")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

SCRIPTS_MARKERS = (
    "## Phase 2",
    "Phase 2 flow - the current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper instead of widening back into older shared reminder churn",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, `zig test scripts/zigux/fixdep.zig`, and `make -C zigux phase2-fixdep` replay the shipped fixdep lane without widening into unrelated Phase 2 surfaces",
)

MAKEFILE_LINES = (
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

REQUIRED_FILES = (
    SCRIPTS_README,
    MAKEFILE,
    FIXDEP_GATE,
    FIXDEP_DIFF,
    FIXDEP_ZIG,
    FIXDEP_CASES,
    WORKFLOW,
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def missing_markers(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def line_count(text: str, line: str) -> int:
    return sum(1 for candidate in text.splitlines() if candidate.strip() == line)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            issues.append(("MISSING_REQUIRED_FILE", str(rel)))

    if not (root / SCRIPTS_README).is_file() or not (root / MAKEFILE).is_file():
        return issues

    scripts_readme = read_text(root, SCRIPTS_README)
    for marker in missing_markers(scripts_readme, SCRIPTS_MARKERS):
        issues.append(("MISSING_SCRIPTS_README_MARKER", marker))

    makefile = read_text(root, MAKEFILE)
    for expected in MAKEFILE_LINES:
        count = line_count(makefile, expected)
        if count != 1:
            issues.append(("MAKEFILE_LINE_COUNT_MISMATCH", f"{count}::{expected}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    for code, detail in issues:
        print(f"PHASE2_SCRIPTS_README_FIXDEP_PACKET_{code}={detail}")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root, SCRIPTS_README, "\n".join(SCRIPTS_MARKERS) + "\n")
    write_text(root, MAKEFILE, "\n".join(MAKEFILE_LINES) + "\n")
    write_text(root, FIXDEP_GATE, "# sample fixdep governance guard\n")
    write_text(root, FIXDEP_DIFF, "# sample fixdep parity checker\n")
    write_text(root, FIXDEP_ZIG, "// sample fixdep helper\n")
    write_text(root, FIXDEP_CASES, "[]\n")
    write_text(root, WORKFLOW, "# sample workflow\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_scripts_readme_fixdep_") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        issues = collect_issues(root)
        if issues:
            raise SystemExit(f"sample root should pass: {issues}")

        write_text(root, SCRIPTS_README, read_text(root, SCRIPTS_README).replace(SCRIPTS_MARKERS[1], "", 1))
        issues = collect_issues(root)
        if ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_MARKERS[1]) not in issues:
            raise SystemExit(f"expected missing scripts marker failure: {issues}")

        build_sample_root(root)
        write_text(root, MAKEFILE, read_text(root, MAKEFILE) + MAKEFILE_LINES[0] + "\n")
        issues = collect_issues(root)
        if ("MAKEFILE_LINE_COUNT_MISMATCH", f"2::{MAKEFILE_LINES[0]}") not in issues:
            raise SystemExit(f"expected duplicate make route failure: {issues}")

        build_sample_root(root)
        (root / FIXDEP_ZIG).unlink()
        issues = collect_issues(root)
        if ("MISSING_REQUIRED_FILE", str(FIXDEP_ZIG)) not in issues:
            raise SystemExit(f"expected missing fixdep helper failure: {issues}")

    print("PHASE2_SCRIPTS_README_FIXDEP_PACKET_SELF_TEST=pass")
    print("PHASE2_SCRIPTS_README_FIXDEP_PACKET_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_SCRIPTS_README_FIXDEP_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_README_FIXDEP_PACKET=pass")
    print(f"PHASE2_SCRIPTS_README_FIXDEP_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_FIXDEP_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_SCRIPTS_README_FIXDEP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
