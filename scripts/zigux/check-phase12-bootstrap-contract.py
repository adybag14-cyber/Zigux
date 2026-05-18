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
    "the current shipped bootstrap lane still declares unfiltered `push` coverage for `master`",
    "the current shipped bootstrap lane still keeps path-filtered `pull_request` coverage for the Zigux-owned lane files",
    "the open trigger-gap investigation is therefore a runtime attachment problem rather than a missing trigger stanza in the committed workflow file",
    "the current shipped bootstrap lane still compiles `scripts/zigux/*.py` before any lane checks run",
    "the current shipped lane still keeps the pinned Zig archive check and the Phase 11 build-inventory plus matrix-gap survey checks",
    "the current shipped Phase 12 slice still includes the build-only surface pair, the release-readiness pair, `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
    "the current shipped lane still runs `make -C zigux phase8-validate` and the focused Phase 8 libbpf segment survey after the Phase 12 complex driver tests",
    "the current shipped bootstrap lane still ends with the inline `Check current docs-root sanity markers` block",
    "the inline docs-root sanity block still checks `Documentation/zigux/README.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `zigux/tests/README.md`, and `scripts/zigux/check-build-only-phase12-surface.py`",
    "dedicated `check-phase12-bootstrap-docs-sanity.py` and `check-phase12-bootstrap-lane-shape.py` guards remain review-only Lane 05 work, not shipped `master` behavior",
]

REQUIRED_STEP_ORDER = [
    "Compile current scripts",
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy packet",
    "Check current pinned Zig archive packet",
    "Self-test current Phase 2 kconfig bridge checker",
    "Check current Phase 2 shared reminder packet",
    "Self-test current Phase 10 bootstrap route checker",
    "Validate Phase 10 checker-backed review packet",
    "Run Phase 10 helper tests",
    "Self-test current Phase 11 HVC cleanup current-head checker",
    "Check current Phase 11 build inventory packet",
    "Check current Phase 11 matrix-gap survey packet",
    "Self-test current Phase 12 build-only surface checker",
    "Check current Phase 12 build-only surface",
    "Self-test current Phase 12 release-readiness packet checker",
    "Validate Phase 12 degraded-workflow bundle",
    "Check current Phase 12 release-readiness packet",
    "Run focused Phase 12 smoke shard",
    "Run Phase 12 complex driver tests",
    "Validate Phase 8 tooling gates",
    "Run focused Phase 8 libbpf segment survey tests",
    "Check current docs-root sanity markers",
]

WORKFLOW_REQUIRED_MARKERS = [
    "workflow_dispatch:",
    "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "make -C zigux phase12-validate",
    "make -C zigux phase12-smoke",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "make -C zigux phase8-validate",
    "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    "python3 - <<'PY2'",
    "Path('Documentation/zigux/README.md')",
    "Path('Documentation/zigux/phase12-release-readiness-survey.md')",
    "Path('zigux/tests/README.md')",
    "Path('scripts/zigux/check-build-only-phase12-surface.py')",
    "ZIGUX_BOOTSTRAP_SANITY=pass",
    "ZIGUX_BOOTSTRAP_REQUIRED_FILE_COUNT=",
    "ZIGUX_BOOTSTRAP_MARKER_COUNT=",
]

WORKFLOW_REQUIRED_PULL_REQUEST_PATHS = [
    "- 'Documentation/zigux/**'",
    "- 'scripts/zigux/**'",
    "- '.github/workflows/zigux-bootstrap.yml'",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py",
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


def slice_block(text: str, start_marker: str, end_marker: str) -> str | None:
    start = text.find(start_marker)
    if start == -1:
        return None
    end = text.find(end_marker, start)
    if end == -1:
        return text[start:]
    return text[start:end]


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

    push_block = slice_block(workflow_text, "  push:\n", "  pull_request:\n")
    if push_block is None:
        failures.append("workflow_missing_event:push")
    else:
        if "    branches: [ master ]" not in push_block:
            failures.append("workflow_push_missing_master_branch")
        if "\n    paths:" in push_block:
            failures.append("workflow_push_paths_filter_present")

    pull_request_block = slice_block(
        workflow_text, "  pull_request:\n", "  workflow_dispatch:\n"
    )
    if pull_request_block is None:
        failures.append("workflow_missing_event:pull_request")
    else:
        if "\n    paths:\n" not in pull_request_block:
            failures.append("workflow_pr_missing_paths_filter")
        for marker in WORKFLOW_REQUIRED_PULL_REQUEST_PATHS:
            if marker not in pull_request_block:
                failures.append(f"workflow_pr_required:{marker}")

    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            failures.append(f"workflow_forbidden:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_note() -> str:
    return """# Phase 12 Bootstrap Lane Contract

This note records the shipped Lane 05 bootstrap posture on current `master`
without reopening the live workflow file in the same change.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current shipped bootstrap lane still declares unfiltered `push` coverage for `master`
- the current shipped bootstrap lane still keeps path-filtered `pull_request` coverage for the Zigux-owned lane files
- the open trigger-gap investigation is therefore a runtime attachment problem rather than a missing trigger stanza in the committed workflow file
- the current shipped bootstrap lane still compiles `scripts/zigux/*.py` before any lane checks run
- the current shipped lane still keeps the pinned Zig archive check and the Phase 11 build-inventory plus matrix-gap survey checks
- the current shipped Phase 12 slice still includes the build-only surface pair, the release-readiness pair, `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- the current shipped lane still runs `make -C zigux phase8-validate` and the focused Phase 8 libbpf segment survey after the Phase 12 complex driver tests
- the current shipped bootstrap lane still ends with the inline `Check current docs-root sanity markers` block
- the inline docs-root sanity block still checks `Documentation/zigux/README.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `zigux/tests/README.md`, and `scripts/zigux/check-build-only-phase12-surface.py`
- dedicated `check-phase12-bootstrap-docs-sanity.py` and `check-phase12-bootstrap-lane-shape.py` guards remain review-only Lane 05 work, not shipped `master` behavior
"""


def fixture_workflow() -> str:
    ordered_steps = "\n".join(
        f"      - name: {step}\n        run: echo step-{index}"
        for index, step in enumerate(REQUIRED_STEP_ORDER, start=1)
    )
    return f"""name: zigux-bootstrap
on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'Documentation/zigux/**'
      - 'scripts/zigux/**'
      - '.github/workflows/zigux-bootstrap.yml'
  workflow_dispatch:

concurrency:
  cancel-in-progress: ${{{{ github.ref != 'refs/heads/master' }}}}

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
{ordered_steps}
      - name: Required markers
        run: |
          python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
          python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
          python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test
          make -C zigux phase12-validate
          make -C zigux phase12-smoke
          zig build test --build-file zigux/tests/phase12_build.zig --summary all
          make -C zigux phase8-validate
          zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all
          python3 - <<'PY2'
          required_files = [
              Path('Documentation/zigux/README.md'),
              Path('Documentation/zigux/phase12-release-readiness-survey.md'),
              Path('zigux/tests/README.md'),
              Path('scripts/zigux/check-build-only-phase12-surface.py'),
          ]
          print('ZIGUX_BOOTSTRAP_SANITY=pass')
          print('ZIGUX_BOOTSTRAP_REQUIRED_FILE_COUNT=5')
          print('ZIGUX_BOOTSTRAP_MARKER_COUNT=4')
          PY2
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
                "      - name: Check current Phase 11 matrix-gap survey packet\n"
                "        run: echo step-12\n",
                "",
                1,
            ),
        )
        expect_failure(base, "workflow_missing:Check current Phase 11 matrix-gap survey packet")

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "      - name: Validate Phase 12 degraded-workflow bundle\n"
                "        run: echo step-16\n"
                "      - name: Check current Phase 12 release-readiness packet\n"
                "        run: echo step-17\n",
                "      - name: Check current Phase 12 release-readiness packet\n"
                "        run: echo step-17\n"
                "      - name: Validate Phase 12 degraded-workflow bundle\n"
                "        run: echo step-16\n",
                1,
            ),
        )
        expect_failure(base, "workflow_order:Check current Phase 12 release-readiness packet")

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
            fixture_workflow().replace(
                "ZIGUX_BOOTSTRAP_SANITY=pass", "BOOTSTRAP_SANITY=pass", 1
            ),
        )
        expect_failure(base, "workflow_required:ZIGUX_BOOTSTRAP_SANITY=pass")

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "  push:\n    branches: [ master ]\n",
                "  push:\n    branches: [ master ]\n    paths:\n      - 'Documentation/zigux/**'\n",
                1,
            ),
        )
        expect_failure(base, "workflow_push_paths_filter_present")

        write_text(
            base / WORKFLOW_PATH,
            fixture_workflow().replace(
                "  pull_request:\n    paths:\n",
                "  pull_request:\n",
                1,
            ),
        )
        expect_failure(base, "workflow_pr_missing_paths_filter")

        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_CONTRACT_SELF_TEST_CASE_COUNT=7")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shipped Lane 05 bootstrap contract on current master."
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
