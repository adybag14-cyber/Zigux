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
    "the live bootstrap workflow still keeps exact-head visibility through unfiltered `push` coverage for `master`, path-filtered `pull_request` coverage, and `workflow_dispatch`",
    "the same live workflow now narrows its Phase 12 bootstrap evidence to `Run current Phase 12 throughput-parity anchor` with `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig`",
    "current `master` still materializes `phase12-smoke`, `phase12-test`, and `phase12` in `zigux/Makefile`, but `.github/workflows/zigux-bootstrap.yml` no longer calls those shared routes",
    "the older support-bundle sequence `Self-test Phase 12 build-only surface checker`, `Check Phase 12 build-only surface`, `Self-test Phase 12 release-readiness packet checker`, `Validate Phase 12 degraded-workflow bundle`, `Check Phase 12 release-readiness packet`, `Run focused Phase 12 smoke shard`, and `Run Phase 12 complex driver tests` is not shipped on current `master`",
    "the older Phase 13 through Phase 15 release-discipline route sequence is also no longer shipped on current `master`",
    "`Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` still belong only to open Lane 05 review branches, not current `master`",
    "until same-lane work restacks a fresh workflow packet, the honest Lane 05 contract is that current `master` measures Phase 12 bootstrap viability only through the direct throughput anchor plus the surviving trigger and concurrency envelope",
]

WORKFLOW_REQUIRED_MARKERS = [
    "  push:\n    branches: [ master ]\n  pull_request:\n    paths:",
    "workflow_dispatch:",
    "concurrency:",
    "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    "- name: Check current Phase 11 HVC cleanup current-head packet",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "- name: Run current Phase 12 throughput-parity anchor",
    "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "Self-test Phase 12 build-only surface checker",
    "Check Phase 12 build-only surface",
    "Self-test Phase 12 release-readiness packet checker",
    "Validate Phase 12 degraded-workflow bundle",
    "Check Phase 12 release-readiness packet",
    "Run focused Phase 12 smoke shard",
    "Run Phase 12 complex driver tests",
    "make -C zigux phase12-validate",
    "make -C zigux phase12-smoke",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "make -C zigux phase13-validate",
    "make -C zigux phase13-test",
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "make -C zigux phase14-test",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
]

MAKEFILE_REQUIRED_MARKERS = [
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-smoke phase12-test",
]

MAKEFILE_FORBIDDEN_MARKERS = [
    "phase12-validate:",
    "phase13-validate:",
    "phase13-test:",
    "phase14-validate:",
    "phase14-smoke:",
    "phase14-test:",
    "phase15-validate:",
    "phase15-test:",
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
    for marker in WORKFLOW_REQUIRED_MARKERS:
        if marker not in workflow_text:
            failures.append(f"workflow_required:{marker}")

    phase11_index = workflow_text.find("- name: Check current Phase 11 HVC cleanup current-head packet")
    phase12_index = workflow_text.find("- name: Run current Phase 12 throughput-parity anchor")
    if phase11_index == -1 or phase12_index == -1:
        failures.append("workflow_order:phase11-phase12-anchor")
    elif phase11_index >= phase12_index:
        failures.append("workflow_order:phase11-phase12-anchor")

    makefile_text = read_text(root, MAKEFILE_PATH)
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile_text:
            failures.append(f"makefile_required:{marker}")
    for marker in MAKEFILE_FORBIDDEN_MARKERS:
        if marker in makefile_text:
            failures.append(f"makefile_forbidden:{marker}")

    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            failures.append(f"workflow_forbidden:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_note() -> str:
    return """# Phase 12 Bootstrap Lane Contract

This note records the current Lane 05 bootstrap viability reading on `master`
without reopening the workflow-file packet itself.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the live bootstrap workflow still keeps exact-head visibility through unfiltered `push` coverage for `master`, path-filtered `pull_request` coverage, and `workflow_dispatch`
- the same live workflow now narrows its Phase 12 bootstrap evidence to `Run current Phase 12 throughput-parity anchor` with `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig`
- current `master` still materializes `phase12-smoke`, `phase12-test`, and `phase12` in `zigux/Makefile`, but `.github/workflows/zigux-bootstrap.yml` no longer calls those shared routes
- the older support-bundle sequence `Self-test Phase 12 build-only surface checker`, `Check Phase 12 build-only surface`, `Self-test Phase 12 release-readiness packet checker`, `Validate Phase 12 degraded-workflow bundle`, `Check Phase 12 release-readiness packet`, `Run focused Phase 12 smoke shard`, and `Run Phase 12 complex driver tests` is not shipped on current `master`
- the older Phase 13 through Phase 15 release-discipline route sequence is also no longer shipped on current `master`
- `Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` still belong only to open Lane 05 review branches, not current `master`
- until same-lane work restacks a fresh workflow packet, the honest Lane 05 contract is that current `master` measures Phase 12 bootstrap viability only through the direct throughput anchor plus the surviving trigger and concurrency envelope
"""


def fixture_workflow() -> str:
    return """name: zigux-bootstrap
on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - '.github/workflows/zigux-bootstrap.yml'
  workflow_dispatch:

concurrency:
  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Check current Phase 11 HVC cleanup current-head packet
        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py
      - name: Run current Phase 12 throughput-parity anchor
        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig
"""


def fixture_makefile() -> str:
    return """phase12-smoke:
\t@echo smoke

phase12-test:
\t@echo test

phase12: phase12-smoke phase12-test
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root / NOTE_PATH, fixture_note())
    write_text(root / WORKFLOW_PATH, fixture_workflow())
    write_text(root / MAKEFILE_PATH, fixture_makefile())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-contract-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        write_text(base / NOTE_PATH, fixture_note().replace("- lane owner: `Lane 05`\n", "", 1))
        expect_failure(base, "note:lane owner: `Lane 05`")

        write_fixture_tree(base)
        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "      - name: Run current Phase 12 throughput-parity anchor\n"
                "        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig\n",
                "",
                1,
            ),
        )
        expect_failure(
            base,
            "workflow_required:- name: Run current Phase 12 throughput-parity anchor",
        )

        write_fixture_tree(base)
        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow()
            + "      - name: Validate Phase 12 degraded-workflow bundle\n"
            + "        run: make -C zigux phase12-validate\n",
        )
        expect_failure(
            base,
            "workflow_forbidden:Validate Phase 12 degraded-workflow bundle",
        )

        write_fixture_tree(base)
        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow()
            + "      - name: Validate Phase 13 release-discipline packet\n"
            + "        run: make -C zigux phase13-validate\n",
        )
        expect_failure(base, "workflow_forbidden:make -C zigux phase13-validate")

        write_fixture_tree(base)
        write_text(base / MAKEFILE_PATH, fixture_makefile() + "\nphase12-validate:\n\t@echo validate\n")
        expect_failure(base, "makefile_forbidden:phase12-validate:")

        write_fixture_tree(base)
        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow()
            + "      - name: Self-test current Phase 12 bootstrap lane checker\n"
            + "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test\n",
        )
        expect_failure(
            base,
            "workflow_forbidden:Self-test current Phase 12 bootstrap lane checker",
        )

        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST_CASE_COUNT=6")
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
    print(
        "PHASE12_BOOTSTRAP_CONTRACT_WORKFLOW_MARKER_COUNT="
        f"{len(WORKFLOW_REQUIRED_MARKERS)}"
    )
    print(f"PHASE12_BOOTSTRAP_CONTRACT_MAKEFILE_MARKER_COUNT={len(MAKEFILE_REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
