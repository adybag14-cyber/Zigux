#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
NOTE_PATH = "Documentation/zigux/phase12-bootstrap-lane-contract.md"

NOTE_MARKERS = [
    "`PHASE12_BOOTSTRAP_LANE=active`",
    "lane owner: `Lane 05`",
    "workflow anchor: `.github/workflows/zigux-bootstrap.yml`",
    "checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`",
    "the current bootstrap workflow still begins with `Compile current scripts`",
    "the current Phase 12 slice is a tail contract, not the whole workflow",
    "current upstream bootstrap steps ahead of that tail include the current Zig toolchain checker pair, the Phase 2 kconfig, kbuild, and toolchain-pinning pairs, the Phase 1 direct-owner and string-review pairs plus the bench and shared-reminder checks, and the Phase 4 repo-reality, reversible-delivery, and tests-readme pairs",
    "the current Phase 12 bootstrap tail is limited to `Self-test current Phase 12 build-only checker` followed by `Check current docs-root sanity markers`",
    "the current workflow reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "`make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` are broader Phase 12 routes, not current bootstrap-lane evidence",
]

REQUIRED_STEP_ORDER = [
    "Compile current scripts",
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy surface",
    "Self-test current Phase 2 kconfig bridge checker",
    "Check current Phase 2 kconfig bridge packet",
    "Self-test current Phase 2 kbuild routes checker",
    "Check current Phase 2 kbuild packet",
    "Self-test current Phase 2 toolchain pinning checker",
    "Check current Phase 2 toolchain pinning packet",
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 bench checker",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 4 repo-reality warning checker",
    "Check current Phase 4 repo-reality warning packet",
    "Self-test current Phase 4 reversible-delivery pin checker",
    "Check current Phase 4 reversible-delivery pin packet",
    "Self-test current Phase 4 tests README checker",
    "Check current Phase 4 tests README packet",
    "Self-test current Phase 12 build-only checker",
    "Check current docs-root sanity markers",
]

WORKFLOW_REQUIRED_MARKERS = [
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "make -C zigux phase12-validate",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "make -C zigux phase12-smoke",
    "zig build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "make -C zigux phase12",
    "Check current Phase 12 bootstrap lane shape",
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

    for rel_path in [WORKFLOW_PATH, NOTE_PATH]:
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
    for step in REQUIRED_STEP_ORDER:
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

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_note() -> str:
    return """# Phase 12 Bootstrap Lane Contract

This note records the current Phase 12 portion of the bootstrap workflow without
rewriting the broader reminder packet or the in-flight workflow restack branch.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current bootstrap workflow still begins with `Compile current scripts`
- the current Phase 12 slice is a tail contract, not the whole workflow
- current upstream bootstrap steps ahead of that tail include the current Zig toolchain checker pair, the Phase 2 kconfig, kbuild, and toolchain-pinning pairs, the Phase 1 direct-owner and string-review pairs plus the bench and shared-reminder checks, and the Phase 4 repo-reality, reversible-delivery, and tests-readme pairs
- the current Phase 12 bootstrap tail is limited to `Self-test current Phase 12 build-only checker` followed by `Check current docs-root sanity markers`
- the current workflow reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` are broader Phase 12 routes, not current bootstrap-lane evidence
- until the workflow widens again, Lane 05 should keep reminder notes and fail-closed checks aligned to this smaller Phase 12 tail instead of treating the broader Phase 12 packet as shipped bootstrap behavior
"""


def fixture_workflow() -> str:
    steps = "\n".join(
        f"      - name: {step}\n        run: echo {index}"
        for index, step in enumerate(REQUIRED_STEP_ORDER, start=1)
    )
    return (
        "name: zigux-bootstrap\n\njobs:\n  bootstrap:\n    runs-on: ubuntu-latest\n"
        "    steps:\n"
        f"{steps}\n"
        "      - name: Phase12 self-test command\n"
        "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test\n"
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-contract-"))
    try:
        write_text(base / NOTE_PATH, fixture_note())
        write_text(base / WORKFLOW_PATH, fixture_workflow())
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
                "Self-test current Phase 12 build-only checker",
                "Self-test current Phase 12 build-only packet",
                1,
            ),
        )
        expect_failure(base, "workflow_missing:Self-test current Phase 12 build-only checker")

        write_text(base / WORKFLOW_PATH, fixture_workflow() + "\n      - name: Validate Phase 12 degraded-workflow bundle\n        run: make -C zigux phase12-validate\n")
        expect_failure(base, "workflow_forbidden:make -C zigux phase12-validate")

        write_text(base / WORKFLOW_PATH, fixture_workflow())
        swapped = read_text(base, WORKFLOW_PATH).replace(
            "      - name: Self-test current Phase 2 kbuild routes checker\n        run: echo 6\n      - name: Check current Phase 2 kbuild packet\n        run: echo 7\n",
            "      - name: Check current Phase 2 kbuild packet\n        run: echo 7\n      - name: Self-test current Phase 2 kbuild routes checker\n        run: echo 6\n",
            1,
        )
        write_text(base / WORKFLOW_PATH, swapped)
        expect_failure(base, "workflow_order:Check current Phase 2 kbuild packet")

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
    print(f"PHASE12_BOOTSTRAP_CONTRACT_STEP_COUNT={len(REQUIRED_STEP_ORDER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
