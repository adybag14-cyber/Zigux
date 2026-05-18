#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / ".github/workflows/zigux-bootstrap.yml").exists() and (
            candidate / "Documentation/zigux/phase12-release-readiness-survey.md"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
DOCS_SANITY_CHECKER_PATH = "scripts/zigux/check-phase12-bootstrap-docs-sanity.py"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"

REQUIRED_FILES = [
    WORKFLOW_PATH,
    SURVEY_PATH,
    DOCS_SANITY_CHECKER_PATH,
    BUILD_ONLY_CHECKER_PATH,
]

WORKFLOW_STEP_NAMES = [
    "Checkout",
    "Setup Python",
    "Setup pinned Zig toolchain",
    "Compile current scripts",
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy packet",
    "Check current pinned Zig archive packet",
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
    "Self-test current kconfig bridge checker",
    "Check current kconfig bridge packet",
    "Run current Phase 2 confdata bridge unit tests",
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
    "Self-test current Phase 3 interop packet",
    "Check current Phase 3 interop packet",
    "Self-test current Phase 3 low-level wrapper survey validator",
    "Check current Phase 3 low-level wrapper survey packet",
    "Run current Phase 3 low-level wrapper replay",
    "Run current Phase 3 shared tests-root packet",
    "Run current Phase 1 shared tests-root smoke",
    "Self-test current Phase 4 repo-reality warning checker",
    "Check current Phase 4 repo-reality warning packet",
    "Self-test current Phase 4 reversible-delivery pin checker",
    "Check current Phase 4 reversible-delivery pin packet",
    "Self-test current Phase 4 tests README checker",
    "Check current Phase 4 tests README packet",
    "Self-test current Phase 4 artifact-diff helper",
    "Self-test current Phase 4 artifact-diff determinism checker",
    "Self-test current Phase 4 artifact-diff validator replay checker",
    "Check current Phase 4 artifact-diff validator replay packet",
    "Self-test current Phase 7 shared-control gap checker",
    "Check current Phase 7 shared-control gap packet",
    "Self-test current Phase 10 bootstrap route checker",
    "Check current Phase 10 bootstrap route",
    "Validate Phase 10 checker-backed review packet",
    "Run Phase 10 helper tests",
    "Self-test current Phase 11 HVC cleanup current-head checker",
    "Check current Phase 11 HVC cleanup current-head packet",
]

WORKFLOW_COMMAND_MARKERS = [
    "# Run every master push so exact-head bootstrap status stays attached even when path filtering misses a live change.",
    "  push:\n    branches: [ master ]\n  pull_request:",
    "workflow_dispatch:",
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "concurrency:",
    "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    "uses: actions/checkout@v6.0.2",
    "fetch-depth: 1",
    "uses: actions/setup-python@v6.2.0",
    "python-version: '3.x'",
    "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test",
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py",
    "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-required-make-routes.py",
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
]

WORKFLOW_EXACT_LINES = [
    "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test",
    "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test",
    "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py",
    "        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "        run: make -C zigux phase10-validate",
]

WORKFLOW_FORBIDDEN_MARKERS = [
    "  push:\n    branches: [ master ]\n    paths:",
    "Check current docs-root sanity markers",
    "ZIGUX_BOOTSTRAP_SANITY=pass",
    "ZIGUX_BOOTSTRAP_REQUIRED_FILE_COUNT=",
    "ZIGUX_BOOTSTRAP_MARKER_COUNT=",
    "python3 - <<'PY2'",
]

SURVEY_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_RELEASE_CLOSED=no`",
    "shared-summary lane owner: `pmo-release`",
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
]


def validate_workflow(workflow_text: str) -> list[str]:
    failures: list[str] = []
    positions: list[int] = []
    workflow_lines = workflow_text.splitlines()

    for step_name in WORKFLOW_STEP_NAMES:
        marker = f"- name: {step_name}"
        position = workflow_text.find(marker)
        if position == -1:
            failures.append(f"workflow_step:{step_name}")
            continue
        positions.append(position)

    if positions and positions != sorted(positions):
        failures.append("workflow_order:bootstrap-step-order")

    for marker in WORKFLOW_COMMAND_MARKERS:
        if marker not in workflow_text:
            failures.append(f"workflow_marker:{marker}")

    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            failures.append(f"workflow_forbidden_marker:{marker}")

    for line in WORKFLOW_EXACT_LINES:
        actual = workflow_lines.count(line)
        if actual != 1:
            failures.append(
                f"workflow_exact_line:{line.strip()}:expected=1:actual={actual}"
            )

    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    workflow_path = root / WORKFLOW_PATH
    if workflow_path.exists():
        workflow_text = workflow_path.read_text(encoding="utf-8")
        failures.extend(validate_workflow(workflow_text))

    survey_path = root / SURVEY_PATH
    if survey_path.exists():
        survey_text = survey_path.read_text(encoding="utf-8")
        for marker in SURVEY_MARKERS:
            if marker not in survey_text:
                failures.append(f"survey:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_workflow() -> str:
    return """name: zigux-bootstrap
# Keep this lane tied to files that the current checkout actually contains.
# Run every master push so exact-head bootstrap status stays attached even when path filtering misses a live change.

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - '.github/workflows/zigux-bootstrap.yml'
  workflow_dispatch:

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

concurrency:
  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6.0.2
        with:
          fetch-depth: 1
      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'
      - name: Setup pinned Zig toolchain
        run: |
          set -euxo pipefail
          curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"
          python3 scripts/zigux/check-zig-toolchain.py --self-test
      - name: Compile current scripts
        run: |
          set -euxo pipefail
          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
      - name: Self-test current Zig toolchain checker
        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
      - name: Check current Zig toolchain policy packet
        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
      - name: Check current pinned Zig archive packet
        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
      - name: Self-test current Phase 12 bootstrap docs sanity checker
        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test
      - name: Check current Phase 12 docs-root sanity markers
        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py
      - name: Self-test current Phase 12 bootstrap lane checker
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test
      - name: Check current Phase 12 bootstrap lane shape
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py
      - name: Self-test current kconfig bridge checker
        run: python3 scripts/zigux/check-kconfig-bridge.py --self-test
      - name: Check current kconfig bridge packet
        run: python3 scripts/zigux/check-kconfig-bridge.py
      - name: Run current Phase 2 confdata bridge unit tests
        run: zig test scripts/zigux/kconfig/confdata_bridge.zig
      - name: Self-test current Phase 2 kconfig bridge checker
        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test
      - name: Check current Phase 2 kconfig bridge packet
        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py
      - name: Self-test current Phase 2 kbuild routes checker
        run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test
      - name: Check current Phase 2 kbuild packet
        run: python3 scripts/zigux/check-phase2-kbuild-routes.py
      - name: Self-test current Phase 2 tests README checker
        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test
      - name: Check current Phase 2 tests README packet
        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py
      - name: Self-test current Phase 2 cross selftest alignment checker
        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test
      - name: Check current Phase 2 cross alignment packet
        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py
      - name: Self-test current Phase 2 toolchain pinning checker
        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test
      - name: Check current Phase 2 toolchain pinning packet
        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py
      - name: Self-test current Phase 2 toolchain pin-scope checker
        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test
      - name: Check current Phase 2 toolchain pin-scope packet
        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py
      - name: Self-test current Phase 2 required-make-routes checker
        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test
      - name: Check current Phase 2 required-make-routes packet
        run: python3 scripts/zigux/check-phase2-required-make-routes.py
      - name: Self-test current Phase 2 shared reminder checker
        run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test
      - name: Check current Phase 2 shared reminder packet
        run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py
      - name: Validate current Phase 2 tool packet
        run: python3 scripts/zigux/validate-phase2.py
      - name: Self-test current Phase 1 direct-owner checker
        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
      - name: Check current Phase 1 direct-owner markers
        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
      - name: Self-test current Phase 1 string review checker
        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test
      - name: Check current Phase 1 string review packet
        run: python3 scripts/zigux/check-phase1-string-review-packet.py
      - name: Self-test current Phase 1 bench checker
        run: python3 scripts/zigux/check-phase1-bench.py --self-test
      - name: Self-test current Phase 1 shared reminder checker
        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
      - name: Check current Phase 1 shared reminder packet
        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py
      - name: Self-test current Phase 3 interop packet
        run: python3 scripts/zigux/validate_phase3_selftest.py
      - name: Check current Phase 3 interop packet
        run: python3 scripts/zigux/run-phase3-checks.py
      - name: Self-test current Phase 3 low-level wrapper survey validator
        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test
      - name: Check current Phase 3 low-level wrapper survey packet
        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py
      - name: Run current Phase 3 low-level wrapper replay
        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig
      - name: Run current Phase 3 shared tests-root packet
        run: zig build phase3-test --build-file zigux/tests/build.zig
      - name: Run current Phase 1 shared tests-root smoke
        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
      - name: Self-test current Phase 4 repo-reality warning checker
        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test
      - name: Check current Phase 4 repo-reality warning packet
        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py
      - name: Self-test current Phase 4 reversible-delivery pin checker
        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test
      - name: Check current Phase 4 reversible-delivery pin packet
        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py
      - name: Self-test current Phase 4 tests README checker
        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test
      - name: Check current Phase 4 tests README packet
        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py
      - name: Self-test current Phase 4 artifact-diff helper
        run: python3 scripts/zigux/artifact_diff.py --self-test
      - name: Self-test current Phase 4 artifact-diff determinism checker
        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
      - name: Self-test current Phase 4 artifact-diff validator replay checker
        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test
      - name: Check current Phase 4 artifact-diff validator replay packet
        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py
      - name: Self-test current Phase 7 shared-control gap checker
        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
      - name: Check current Phase 7 shared-control gap packet
        run: python3 scripts/zigux/check-phase7-shared-control-gap.py
      - name: Self-test current Phase 10 bootstrap route checker
        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
      - name: Check current Phase 10 bootstrap route
        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
      - name: Validate Phase 10 checker-backed review packet
        run: make -C zigux phase10-validate
      - name: Run Phase 10 helper tests
        run: make -C zigux phase10-test
      - name: Self-test current Phase 11 HVC cleanup current-head checker
        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test
      - name: Check current Phase 11 HVC cleanup current-head packet
        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py
"""


def minimal_survey() -> str:
    return """# Phase 12 Release Readiness Survey

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared-summary lane owner: `pmo-release`
- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root / WORKFLOW_PATH, minimal_workflow())
    write_text(root / SURVEY_PATH, minimal_survey())
    write_text(root / DOCS_SANITY_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write_text(root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-lane-shape-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / DOCS_SANITY_CHECKER_PATH).unlink()
        expect_failure(base, f"missing_file:{DOCS_SANITY_CHECKER_PATH}")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Self-test current Phase 12 bootstrap docs sanity checker\n"
                "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_step:Self-test current Phase 12 bootstrap docs sanity checker")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Self-test current Phase 4 artifact-diff helper\n"
                "        run: python3 scripts/zigux/artifact_diff.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_step:Self-test current Phase 4 artifact-diff helper")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "  push:\n    branches: [ master ]\n  pull_request:\n",
                "  push:\n    branches: [ master ]\n    paths:\n      - '.github/workflows/zigux-bootstrap.yml'\n  pull_request:\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "workflow_forbidden_marker:  push:\n    branches: [ master ]\n    paths:",
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py\n",
                "        run: echo skip-lane-shape\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "workflow_exact_line:run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py:expected=1:actual=0",
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_text = workflow_path.read_text(encoding="utf-8")
        docs_block = (
            "      - name: Self-test current Phase 12 bootstrap docs sanity checker\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test\n"
            "      - name: Check current Phase 12 docs-root sanity markers\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py\n"
        )
        swapped_block = (
            "      - name: Check current Phase 12 docs-root sanity markers\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py\n"
            "      - name: Self-test current Phase 12 bootstrap docs sanity checker\n"
            "        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test\n"
        )
        workflow_path.write_text(
            workflow_text.replace(docs_block, swapped_block, 1),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_order:bootstrap-step-order")

        write_fixture_tree(base)
        survey_path = base / SURVEY_PATH
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "- `PHASE12_RELEASE_CLOSED=no`\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, "survey:`PHASE12_RELEASE_CLOSED=no`")

        print("PHASE12_BOOTSTRAP_LANE_SHAPE_SELF_TEST=pass")
        print("PHASE12_BOOTSTRAP_LANE_SHAPE_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 bootstrap workflow lane so the "
            "workflow keeps the shipped exact-head push trigger, the newer "
            "Phase 2, Phase 1, Phase 3, Phase 4 artifact-diff, Phase 7, "
            "Phase 10, and Phase 11 guards, and the dedicated docs-sanity "
            "checks reviewable on current master."
        )
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
            print(f"PHASE12_BOOTSTRAP_LANE_SHAPE=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_BOOTSTRAP_LANE_SHAPE=pass")
    print(f"PHASE12_BOOTSTRAP_LANE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_BOOTSTRAP_LANE_MARKER_COUNT="
        f"{len(WORKFLOW_STEP_NAMES) + len(WORKFLOW_COMMAND_MARKERS) + len(WORKFLOW_EXACT_LINES) + len(SURVEY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
