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
TESTS_README_PATH = "zigux/tests/README.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"

REQUIRED_FILES = [
    WORKFLOW_PATH,
    SURVEY_PATH,
    TESTS_README_PATH,
    BUILD_ONLY_CHECKER_PATH,
]

WORKFLOW_MARKERS = [
    "Compile current scripts",
    "Self-test current Phase 12 build-only checker",
    "Self-test current Phase 12 bootstrap lane checker",
    "Check current Phase 12 bootstrap lane shape",
    "Check current docs-root sanity markers",
]

SURVEY_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_RELEASE_CLOSED=no`",
    "shared-summary lane owner: `pmo-release`",
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
]


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    workflow_path = root / WORKFLOW_PATH
    if workflow_path.exists():
        workflow_text = workflow_path.read_text(encoding="utf-8")
        for marker in WORKFLOW_MARKERS:
            if marker not in workflow_text:
                failures.append(f"workflow:{marker}")

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
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Compile current scripts
        run: python3 -m py_compile scripts/zigux/*.py
      - name: Self-test current Phase 12 build-only checker
        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
      - name: Self-test current Phase 12 bootstrap lane checker
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py --self-test
      - name: Check current Phase 12 bootstrap lane shape
        run: python3 scripts/zigux/check-phase12-bootstrap-lane-shape.py
      - name: Check current docs-root sanity markers
        run: python3 - <<'PY'
        print('ok')
        PY
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
    write_text(root / TESTS_README_PATH, "# zigux/tests\n")
    write_text(root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-bootstrap-lane-shape-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / BUILD_ONLY_CHECKER_PATH).unlink()
        expect_failure(base, f"missing_file:{BUILD_ONLY_CHECKER_PATH}")

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "Check current Phase 12 bootstrap lane shape", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow:Check current Phase 12 bootstrap lane shape")

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
        print("PHASE12_BOOTSTRAP_LANE_SHAPE_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the small current Phase 12 bootstrap lane so the workflow "
            "keeps checking the live build-only contract and docs-root survey markers."
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
    print(f"PHASE12_BOOTSTRAP_LANE_MARKER_COUNT={len(WORKFLOW_MARKERS) + len(SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
