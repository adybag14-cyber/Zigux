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
    "current workflow evidence starts with `Compile current scripts`",
    "current Phase 12 bootstrap evidence is limited to `Self-test current Phase 12 build-only checker`",
    "the current workflow reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "the current workflow ends the Phase 12 bootstrap slice at `Check current docs-root sanity markers`",
    "`make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` are broader Phase 12 routes, not current bootstrap-lane evidence",
]

WORKFLOW_MARKERS = [
    "Compile current scripts",
    "Self-test current Phase 12 build-only checker",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "Check current docs-root sanity markers",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "make -C zigux phase12-validate",
    "make -C zigux phase12-smoke",
    "zig build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
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
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow_text:
            failures.append(f"workflow:{marker}")

    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            failures.append(f"workflow_forbidden:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_note() -> str:
    return """# Phase 12 Bootstrap Lane Contract

This note records the narrow Phase 12 bootstrap contract that current `master`
actually runs in `.github/workflows/zigux-bootstrap.yml`.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- current workflow evidence starts with `Compile current scripts`
- current Phase 12 bootstrap evidence is limited to `Self-test current Phase 12 build-only checker`
- the current workflow reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- the current workflow ends the Phase 12 bootstrap slice at `Check current docs-root sanity markers`
- `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` are broader Phase 12 routes, not current bootstrap-lane evidence
- until the workflow widens again, Lane 05 should keep reminder notes and small fail-closed checks aligned to this smaller sanity lane instead of treating the broader Phase 12 packet as shipped bootstrap behavior
"""


def fixture_workflow() -> str:
    return """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Compile current scripts
        run: python3 -m py_compile scripts/zigux/check-build-only-phase12-surface.py

      - name: Self-test current Phase 12 build-only checker
        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test

      - name: Check current docs-root sanity markers
        run: python3 - <<'PY'
          print(\"ok\")
          PY
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-contract-"))
    try:
        write_text(base / NOTE_PATH, fixture_note())
        write_text(base / WORKFLOW_PATH, fixture_workflow())
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_text(base / WORKFLOW_PATH, fixture_workflow())
        write_text(base / NOTE_PATH, fixture_note().replace("- lane owner: `Lane 05`\n", "", 1))
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
        expect_failure(base, "workflow:Self-test current Phase 12 build-only checker")

        write_text(base / WORKFLOW_PATH, fixture_workflow() + "\n      - name: Validate Phase 12 degraded-workflow bundle\n        run: make -C zigux phase12-validate\n")
        expect_failure(base, "workflow_forbidden:make -C zigux phase12-validate")

        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST_CASE_COUNT=3")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the narrow Phase 12 bootstrap contract against the current workflow and note."
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
    print(f"PHASE12_BOOTSTRAP_CONTRACT_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
