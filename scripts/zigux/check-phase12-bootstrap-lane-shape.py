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
    "Compile current scripts",
    "Self-test current Phase 12 build-only checker",
    "Check current Phase 12 build-only surface",
    "Self-test current Phase 12 bootstrap docs sanity checker",
    "Check current Phase 12 docs-root sanity markers",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
]

WORKFLOW_COMMAND_MARKERS = [
    "workflow_dispatch:",
    "concurrency:",
    "group: ${{ github.ref == 'refs/heads/master'",
    "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "python-version: '3.x'",
    "set -euxo pipefail",
    "find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test",
    "python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test",
    "python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py",
]

WORKFLOW_EXACT_LINES = [
    "        run: python3 scripts/zigux/check-build-only-phase12-surface.py",
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
on:
  workflow_dispatch:

concurrency:
  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6.0.2
      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'
      - name: Compile current scripts
        run: |
          set -euxo pipefail
          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
          python3 -m py_compile \"${scripts[@]}\"
      - name: Self-test current Phase 12 build-only checker
        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
      - name: Check current Phase 12 build-only surface
        run: python3 scripts/zigux/check-build-only-phase12-surface.py
      - name: Self-test current Phase 12 bootstrap docs sanity checker
        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py --self-test
      - name: Check current Phase 12 docs-root sanity markers
        run: python3 scripts/zigux/check-phase12-bootstrap-docs-sanity.py
      - name: Self-test current Phase 12 bootstrap lane checker
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test
      - name: Check current Phase 12 bootstrap lane shape
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py
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
                "- name: Check current Phase 12 build-only surface\n"
                "        run: python3 scripts/zigux/check-build-only-phase12-surface.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_step:Check current Phase 12 build-only surface")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-build-only-phase12-surface.py\n",
                "        run: echo skip-build-only\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "workflow_exact_line:run: python3 scripts/zigux/check-build-only-phase12-surface.py:expected=1:actual=0",
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "- name: Setup Python\n"
                "        uses: actions/setup-python@v6.2.0\n"
                "        with:\n"
                "          python-version: '3.x'\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_step:Setup Python")

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
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "  workflow_dispatch:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow_marker:workflow_dispatch:")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "workflow_marker:cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
        )

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
        print("PHASE12_BOOTSTRAP_LANE_SHAPE_SELF_TEST_CASE_COUNT=8")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the small current Phase 12 bootstrap lane so the workflow "
            "keeps checking the live build-only contract, docs-root survey markers, "
            "manual dispatch hook, and concurrency guard."
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