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
    "the shipped bootstrap lane still compiles `scripts/zigux/*.py` before any workflow guards run",
    "the shipped lane still keeps the Zig toolchain self-test, policy, and pinned-archive checks together at the top of the workflow",
    "the shipped lane still keeps the current Phase 2 kconfig, tests README, cross-selftest, toolchain-pinning, toolchain pin-scope, required-make-routes, shared-reminder, and `validate-phase2.py` packet intact",
    "the shipped lane still keeps the current Phase 1 direct-owner, string-review, bench self-test, shared-reminder, and shared tests-root smoke packet intact",
    "the shipped lane still keeps the current Phase 4 repo-reality, reversible-delivery, and tests README packet intact",
    "the shipped lane still keeps the current Phase 7 shared-control gap packet intact",
    "the shipped lane still keeps the current Phase 10 bootstrap-route pair plus `make -C zigux phase10-validate` and `make -C zigux phase10-test`",
    "the shipped lane currently ends with the Phase 11 HVC cleanup current-head pair",
    "no shipped Phase 12 or Phase 8 tail remains on current `master`",
    "no shipped inline `Check current docs-root sanity markers` block remains on current `master`",
    "review-only Lane 05 packets such as `check-phase12-bootstrap-docs-sanity.py`, `check-phase12-bootstrap-lane-shape.py`, and this contract checker are still unmerged on current `master`",
]

REQUIRED_STEP_ORDER = [
    "Compile current scripts",
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy packet",
    "Check current pinned Zig archive packet",
    "Self-test current Phase 2 kconfig bridge checker",
    "Check current Phase 2 kconfig bridge packet",
    "Self-test current Phase 2 kbuild routes checker",
    "Check current Phase 2 kbuild packet",
    "Self-test current Phase 2 tests README checker",
    "Check current Phase 2 tests README packet",
    "Self-test current Phase 2 cross selftest alignment checker",
    "Check current Phase 2 cross alignment packet",
    "Self-test current Phase 2 toolchain pinning checker",
    "Check current Phase 2 toolchain pinning packet",
    "Self-test current Phase 2 toolchain pin-scope checker",
    "Check current Phase 2 toolchain pin-scope packet",
    "Self-test current Phase 2 required-make-routes checker",
    "Check current Phase 2 required-make-routes packet",
    "Self-test current Phase 2 shared reminder checker",
    "Check current Phase 2 shared reminder packet",
    "Validate current Phase 2 tool packet",
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 bench checker",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Run current Phase 1 shared tests-root smoke",
    "Self-test current Phase 4 repo-reality warning checker",
    "Check current Phase 4 repo-reality warning packet",
    "Self-test current Phase 4 reversible-delivery pin checker",
    "Check current Phase 4 reversible-delivery pin packet",
    "Self-test current Phase 4 tests README checker",
    "Check current Phase 4 tests README packet",
    "Self-test current Phase 7 shared-control gap checker",
    "Check current Phase 7 shared-control gap packet",
    "Self-test current Phase 10 bootstrap route checker",
    "Check current Phase 10 bootstrap route",
    "Validate Phase 10 checker-backed review packet",
    "Run Phase 10 helper tests",
    "Self-test current Phase 11 HVC cleanup current-head checker",
    "Check current Phase 11 HVC cleanup current-head packet",
]

WORKFLOW_REQUIRED_MARKERS = [
    "workflow_dispatch:",
    "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    "find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
    "Self-test current Phase 12 release-readiness packet checker",
    "Validate Phase 12 degraded-workflow bundle",
    "Run focused Phase 12 smoke shard",
    "Run Phase 12 complex driver tests",
    "Validate Phase 8 tooling gates",
    "Run focused Phase 8 libbpf segment survey tests",
    "Check current docs-root sanity markers",
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "make -C zigux phase12-validate",
    "make -C zigux phase12-smoke",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "make -C zigux phase8-validate",
    "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    "python3 - <<'PY2'",
    "ZIGUX_BOOTSTRAP_SANITY=pass",
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
        current_index = workflow_text.find(f"- name: {step}")
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

This note records the current Lane 05 bootstrap posture on shipped `master`
without reopening the live workflow file in the same change.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the shipped bootstrap lane still compiles `scripts/zigux/*.py` before any workflow guards run
- the shipped lane still keeps the Zig toolchain self-test, policy, and pinned-archive checks together at the top of the workflow
- the shipped lane still keeps the current Phase 2 kconfig, tests README, cross-selftest, toolchain-pinning, toolchain pin-scope, required-make-routes, shared-reminder, and `validate-phase2.py` packet intact
- the shipped lane still keeps the current Phase 1 direct-owner, string-review, bench self-test, shared-reminder, and shared tests-root smoke packet intact
- the shipped lane still keeps the current Phase 4 repo-reality, reversible-delivery, and tests README packet intact
- the shipped lane still keeps the current Phase 7 shared-control gap packet intact
- the shipped lane still keeps the current Phase 10 bootstrap-route pair plus `make -C zigux phase10-validate` and `make -C zigux phase10-test`
- the shipped lane currently ends with the Phase 11 HVC cleanup current-head pair
- no shipped Phase 12 or Phase 8 tail remains on current `master`
- no shipped inline `Check current docs-root sanity markers` block remains on current `master`
- review-only Lane 05 packets such as `check-phase12-bootstrap-docs-sanity.py`, `check-phase12-bootstrap-lane-shape.py`, and this contract checker are still unmerged on current `master`
"""


def fixture_workflow() -> str:
    ordered_steps = "\n".join(
        f"      - name: {step}\n        run: echo step-{index}"
        for index, step in enumerate(REQUIRED_STEP_ORDER, start=1)
    )
    required_marker_block = """      - name: Required markers
        run: |
          find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort
          python3 scripts/zigux/check-zig-toolchain.py --self-test
          python3 scripts/zigux/check-zig-toolchain.py --policy-only
          python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
          python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test
          python3 scripts/zigux/check-phase2-required-make-routes.py --self-test
          python3 scripts/zigux/validate-phase2.py
          python3 scripts/zigux/check-phase1-bench.py --self-test
          zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
          make -C zigux phase10-validate
          make -C zigux phase10-test
          python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test
          python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py
"""
    return f"""name: zigux-bootstrap
on:
  workflow_dispatch:

concurrency:
  cancel-in-progress: ${{{{ github.ref != 'refs/heads/master' }}}}

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
{ordered_steps}
{required_marker_block}"""


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
                "      - name: Check current Phase 11 HVC cleanup current-head packet\n"
                "        run: echo step-43\n",
                "",
                1,
            ),
        )
        expect_failure(
            base, "workflow_missing:Check current Phase 11 HVC cleanup current-head packet"
        )

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "      - name: Validate Phase 10 checker-backed review packet\n"
                "        run: echo step-40\n"
                "      - name: Run Phase 10 helper tests\n"
                "        run: echo step-41\n",
                "      - name: Run Phase 10 helper tests\n"
                "        run: echo step-41\n"
                "      - name: Validate Phase 10 checker-backed review packet\n"
                "        run: echo step-40\n",
                1,
            ),
        )
        expect_failure(base, "workflow_order:Run Phase 10 helper tests")

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow()
            + "      - name: Self-test current Phase 12 bootstrap docs sanity checker\n"
            + "        run: echo stale\n",
        )
        expect_failure(
            base,
            "workflow_forbidden:Self-test current Phase 12 bootstrap docs sanity checker",
        )

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace("make -C zigux phase10-test", "echo skip-phase10-test", 1),
        )
        expect_failure(base, "workflow_required:make -C zigux phase10-test")

        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Lane 05 bootstrap contract on shipped master."
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
