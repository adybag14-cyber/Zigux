#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
NOTE_PATH = "Documentation/zigux/phase12-bootstrap-lane-contract.md"

NOTE_MARKERS = [
    "`PHASE12_BOOTSTRAP_LANE=active`",
    "lane owner: `Lane 05`",
    "workflow anchor: `.github/workflows/zigux-bootstrap.yml`",
    "checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`",
    "the current bootstrap workflow now keeps the shared Phase 12 packet explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
    "the same live bootstrap workflow now continues straight into `make -C zigux phase13-validate`, `make -C zigux phase13-test`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase15-validate`, and `make -C zigux phase15-test`",
    "current `master` no longer materializes `phase12-validate`, `phase12-smoke`, `phase12-test`, `phase12`, `phase13-validate`, `phase13-test`, `phase13`, `phase14-validate`, `phase14-smoke`, `phase14-test`, `phase14`, `phase15-validate`, `phase15-test`, or `phase15` in `zigux/Makefile`, so those bootstrap route names are a live Lane 05 workflow-viability gap rather than shipped current-`master` evidence",
    "until same-lane work rematerializes those shared Make routes, the honest contract is that `.github/workflows/zigux-bootstrap.yml` overstates current shared Phase 12 through Phase 15 route viability",
    "`Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` still belong only to the open Lane 05 review branches, not current `master`",
]

WORKFLOW_STEP_ORDER = [
    "Self-test Phase 12 build-only surface checker",
    "Check Phase 12 build-only surface",
    "Self-test Phase 12 release-readiness packet checker",
    "Validate Phase 12 degraded-workflow bundle",
    "Check Phase 12 release-readiness packet",
    "Run focused Phase 12 smoke shard",
    "Run Phase 12 complex driver tests",
    "Validate Phase 13 release-discipline packet",
    "Run Phase 13 shared helper tests",
    "Validate Phase 14 shared smoke packet",
    "Run focused Phase 14 smoke shard",
    "Run Phase 14 internal bridge tests",
    "Validate Phase 15 governance packet",
    "Run Phase 15 governance tests",
]

WORKFLOW_REQUIRED_MARKERS = [
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "make -C zigux phase12-validate",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "make -C zigux phase12-smoke",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "make -C zigux phase13-validate",
    "make -C zigux phase13-test",
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "make -C zigux phase14-test",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
]

MAKEFILE_FORBIDDEN_MARKERS = [
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "phase13-validate:",
    "phase13-test:",
    "phase13: phase13-validate phase13-test",
    "phase14-validate:",
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
    "phase15-validate:",
    "phase15-test:",
    "phase15: phase15-validate phase15-test",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / WORKFLOW_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    path = root / rel_path
    if not path.exists():
        raise FileNotFoundError(rel_path)
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [WORKFLOW_PATH, MAKEFILE_PATH, NOTE_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    note_text = read_text(root, NOTE_PATH)
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            failures.append(f"note:{marker}")

    workflow_text = read_text(root, WORKFLOW_PATH)
    last_index = -1
    for step in WORKFLOW_STEP_ORDER:
        current_index = workflow_text.find(step)
        if current_index == -1:
            failures.append(f"workflow_missing:{step}")
            continue
        if current_index <= last_index:
            failures.append(f"workflow_order:{step}")
        last_index = current_index

    for marker in WORKFLOW_REQUIRED_MARKERS:
        if marker not in workflow_text:
            failures.append(f"workflow_required:{marker}")

    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            failures.append(f"workflow_forbidden:{marker}")

    makefile_text = read_text(root, MAKEFILE_PATH)
    for marker in MAKEFILE_FORBIDDEN_MARKERS:
        if marker in makefile_text:
            failures.append(f"makefile_forbidden:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_note() -> str:
    return """# Phase 12 Bootstrap Lane Contract

This note records the current Lane 05 bootstrap viability reading on `master`
without widening into a workflow replay.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current bootstrap workflow now keeps the shared Phase 12 packet explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- the same live bootstrap workflow now continues straight into `make -C zigux phase13-validate`, `make -C zigux phase13-test`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase15-validate`, and `make -C zigux phase15-test`
- current `master` no longer materializes `phase12-validate`, `phase12-smoke`, `phase12-test`, `phase12`, `phase13-validate`, `phase13-test`, `phase13`, `phase14-validate`, `phase14-smoke`, `phase14-test`, `phase14`, `phase15-validate`, `phase15-test`, or `phase15` in `zigux/Makefile`, so those bootstrap route names are a live Lane 05 workflow-viability gap rather than shipped current-`master` evidence
- until same-lane work rematerializes those shared Make routes, the honest contract is that `.github/workflows/zigux-bootstrap.yml` overstates current shared Phase 12 through Phase 15 route viability
- `Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` still belong only to the open Lane 05 review branches, not current `master`
"""


def fixture_workflow() -> str:
    steps = []
    for step in WORKFLOW_STEP_ORDER:
        command = "echo ok"
        for marker in WORKFLOW_REQUIRED_MARKERS:
            if step in marker or marker.endswith(step):
                command = marker
                break
        command_map = {
            "Self-test Phase 12 build-only surface checker": "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
            "Check Phase 12 build-only surface": "python3 scripts/zigux/check-build-only-phase12-surface.py",
            "Self-test Phase 12 release-readiness packet checker": "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
            "Validate Phase 12 degraded-workflow bundle": "make -C zigux phase12-validate",
            "Check Phase 12 release-readiness packet": "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
            "Run focused Phase 12 smoke shard": "make -C zigux phase12-smoke",
            "Run Phase 12 complex driver tests": "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
            "Validate Phase 13 release-discipline packet": "make -C zigux phase13-validate",
            "Run Phase 13 shared helper tests": "make -C zigux phase13-test",
            "Validate Phase 14 shared smoke packet": "make -C zigux phase14-validate",
            "Run focused Phase 14 smoke shard": "make -C zigux phase14-smoke",
            "Run Phase 14 internal bridge tests": "make -C zigux phase14-test",
            "Validate Phase 15 governance packet": "make -C zigux phase15-validate",
            "Run Phase 15 governance tests": "make -C zigux phase15-test",
        }
        steps.append(f"      - name: {step}\n        run: {command_map[step]}")
    return "name: zigux-bootstrap\njobs:\n  bootstrap:\n    runs-on: ubuntu-latest\n    steps:\n" + "\n".join(steps) + "\n"


def fixture_makefile() -> str:
    return """PHONY += phase2-toolchain phase2-validate phase2
PHONY += phase8-validate phase8-test phase8
PHONY += phase10-validate phase10-test phase10
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-contract-"))
    try:
        write_text(base / NOTE_PATH, fixture_note())
        write_text(base / WORKFLOW_PATH, fixture_workflow())
        write_text(base / MAKEFILE_PATH, fixture_makefile())
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_text(
            base / NOTE_PATH,
            fixture_note().replace("- lane owner: `Lane 05`\n", "", 1),
        )
        expect_failure(base, "note:lane owner: `Lane 05`")

        write_text(base / NOTE_PATH, fixture_note())
        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "      - name: Validate Phase 13 release-discipline packet\n        run: make -C zigux phase13-validate\n",
                "",
                1,
            ),
        )
        expect_failure(base, "workflow_missing:Validate Phase 13 release-discipline packet")

        write_text(base / WORKFLOW_PATH, fixture_workflow())
        write_text(
            base / MAKEFILE_PATH,
            fixture_makefile() + "phase12-validate:\n",
        )
        expect_failure(base, "makefile_forbidden:phase12-validate:")

        write_text(base / MAKEFILE_PATH, fixture_makefile())
        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow()
            + "      - name: Self-test current Phase 12 bootstrap lane checker\n        run: echo stale\n",
        )
        expect_failure(
            base,
            "workflow_forbidden:Self-test current Phase 12 bootstrap lane checker",
        )

        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 12 bootstrap contract companion."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_BOOTSTRAP_CONTRACT=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_BOOTSTRAP_CONTRACT=pass")
    print(f"PHASE12_BOOTSTRAP_CONTRACT_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE12_BOOTSTRAP_CONTRACT_STEP_COUNT={len(WORKFLOW_STEP_ORDER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
