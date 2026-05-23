#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=productization_gap_survey

Fail-closed checker for the bounded Phase 14 productization-gap survey.

This guard keeps the shared Phase 14 productization note aligned with the live
study-only packet on current `master` without promoting the missing executable
layer or broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=productization_gap_survey"

DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
RCU_TREE_SURVEY_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
TESTS_README_CHECKER_PATH = Path("scripts/zigux/check-phase14-tests-readme-smoke-summary.py")
ROLLBACK_THRESHOLD_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
)
RCU_GUARDRAIL_CHECKER_PATH = Path("scripts/zigux/check-phase14-rcu-rollback-guardrail.py")
RELEASE_BOUNDARY_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
)
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")

TESTS_PHASE14_START = "## Phase 14 shared smoke packet"
TESTS_PHASE14_END = "## Phase 15 governance packet"

REQUIRED_FILES = (
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    PRODUCTIZATION_GAP_PATH,
    RCU_TREE_SURVEY_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    TESTS_README_CHECKER_PATH,
    ROLLBACK_THRESHOLD_CHECKER_PATH,
    RCU_GUARDRAIL_CHECKER_PATH,
    RELEASE_BOUNDARY_CHECKER_PATH,
    VALIDATOR_PATH,
)

REQUIRED_PRODUCTIZATION_MARKERS = (
    "Roadmap expectations for this lane:",
    "- boundary maps",
    "- concurrency audits",
    "- explicit stay-in-C decisions where warranted",
    "- wrapper-first or study-only posture",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py` now returns through the current contents path",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py` now returns through the current contents path",
    "`scripts/zigux/check-phase14-rcu-rollback-guardrail.py` now returns through the current contents path",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path",
    "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
    "the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "`Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, and `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` beside the already-recovered shared smoke packet members",
)

REQUIRED_DOCS_README_MARKERS = (
    "Phase 14 notes",
    "`Documentation/zigux/phase14-productization-gap-survey.md`",
    "`Documentation/zigux/phase14-rcu-tree-survey.md`",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
    "`scripts/zigux/check-phase14-rcu-rollback-guardrail.py`",
    "the returned `phase14-validate` split",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 14 smoke packet",
    "`scripts/zigux/validate-phase14.py` and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/Makefile` framed as readable current evidence",
    "`zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` framed as exact-readback gaps",
)

REQUIRED_TESTS_SECTION_MARKERS = (
    "`Documentation/zigux/phase14-productization-gap-survey.md`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "`scripts/zigux/check-phase14-shared-smoke-route.py`",
    "`scripts/zigux/validate-phase14.py`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/Makefile`",
    "`zigux/tests/phase14_workqueue_reviewability.zig`",
    "`zigux/tests/phase14_ring_buffer_survey.zig`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "## Phase 14",
    "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
    "`scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, and `zigux/Makefile` keep the directly readable shared-smoke route proof",
    "shared reminder truthfulness around the returned study-only packet and the single `make -C zigux phase14-validate` gate",
)

REQUIRED_TESTS_CHECKER_MARKERS = (
    "Check that the shared Phase 14 tests-root reminder stays aligned with repo reality.",
    'SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")',
    "\"`Documentation/zigux/phase14-productization-gap-survey.md`\"",
)

REQUIRED_ROLLBACK_CHECKER_MARKERS = (
    "PHASE14_CHECK_PACKET=rollback_threshold_sequencing",
    "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass",
)

REQUIRED_RCU_GUARDRAIL_MARKERS = (
    "PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass",
    "`PHASE14_LANE_KEY=P14-L14`",
)

REQUIRED_RELEASE_CHECKER_MARKERS = (
    "PHASE14_CHECK_PACKET=release_boundary_exact_counts",
    "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass",
)

REQUIRED_VALIDATOR_MARKERS = (
    "PHASE14_VALIDATION=pass",
    'PRODUCTIZATION_GAP_PATH = "Documentation/zigux/phase14-productization-gap-survey.md"',
)

REQUIRED_MAKEFILE_MARKERS = (
    "phase14-validate:",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
    "scripts/zigux/validate-phase14.py --self-test",
    "scripts/zigux/validate-phase14.py",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"missing section start marker: {start_marker}")
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"missing section end marker: {end_marker}")
    return text[start:end]


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(
        errors,
        PRODUCTIZATION_GAP_PATH,
        read_text(root, PRODUCTIZATION_GAP_PATH),
        REQUIRED_PRODUCTIZATION_MARKERS,
    )
    require_markers(
        errors,
        DOCS_README_PATH,
        read_text(root, DOCS_README_PATH),
        REQUIRED_DOCS_README_MARKERS,
    )
    require_markers(
        errors,
        REVIEW_CHECKLIST_PATH,
        read_text(root, REVIEW_CHECKLIST_PATH),
        REQUIRED_REVIEW_CHECKLIST_MARKERS,
    )

    tests_text = read_text(root, TESTS_README_PATH)
    try:
        tests_section = section(tests_text, TESTS_PHASE14_START, TESTS_PHASE14_END)
    except ValueError as exc:
        errors.append(f"section_error:{TESTS_README_PATH.as_posix()}:{exc}")
    else:
        require_markers(errors, TESTS_README_PATH, tests_section, REQUIRED_TESTS_SECTION_MARKERS)

    require_markers(
        errors,
        SCRIPTS_README_PATH,
        read_text(root, SCRIPTS_README_PATH),
        REQUIRED_SCRIPTS_README_MARKERS,
    )
    require_markers(
        errors,
        TESTS_README_CHECKER_PATH,
        read_text(root, TESTS_README_CHECKER_PATH),
        REQUIRED_TESTS_CHECKER_MARKERS,
    )
    require_markers(
        errors,
        ROLLBACK_THRESHOLD_CHECKER_PATH,
        read_text(root, ROLLBACK_THRESHOLD_CHECKER_PATH),
        REQUIRED_ROLLBACK_CHECKER_MARKERS,
    )
    require_markers(
        errors,
        RCU_GUARDRAIL_CHECKER_PATH,
        read_text(root, RCU_GUARDRAIL_CHECKER_PATH),
        REQUIRED_RCU_GUARDRAIL_MARKERS,
    )
    require_markers(
        errors,
        RELEASE_BOUNDARY_CHECKER_PATH,
        read_text(root, RELEASE_BOUNDARY_CHECKER_PATH),
        REQUIRED_RELEASE_CHECKER_MARKERS,
    )
    require_markers(
        errors,
        VALIDATOR_PATH,
        read_text(root, VALIDATOR_PATH),
        REQUIRED_VALIDATOR_MARKERS,
    )

    makefile_text = read_text(root, MAKEFILE_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile_text, REQUIRED_MAKEFILE_MARKERS)
    require_absent(errors, MAKEFILE_PATH, makefile_text, FORBIDDEN_MAKEFILE_MARKERS)
    return errors


def fixture_with_markers(title: str, markers: tuple[str, ...]) -> str:
    return title + "\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(root / PRODUCTIZATION_GAP_PATH, fixture_with_markers("# Phase 14 Productization Gap Survey", REQUIRED_PRODUCTIZATION_MARKERS))
    write_text(root / DOCS_README_PATH, fixture_with_markers("# Zigux Documentation", REQUIRED_DOCS_README_MARKERS))
    write_text(root / REVIEW_CHECKLIST_PATH, fixture_with_markers("# Zigux Review Checklist", REQUIRED_REVIEW_CHECKLIST_MARKERS))
    write_text(
        root / TESTS_README_PATH,
        "# zigux/tests\n\n"
        "## Phase 14 shared smoke packet\n\n"
        + "\n".join(f"- {marker}" for marker in REQUIRED_TESTS_SECTION_MARKERS)
        + "\n\n## Phase 15 governance packet\n",
    )
    write_text(root / SCRIPTS_README_PATH, fixture_with_markers("# scripts/zigux", REQUIRED_SCRIPTS_README_MARKERS))
    write_text(root / RCU_TREE_SURVEY_PATH, "# Phase 14 RCU Tree Survey\n")
    write_text(root / TESTS_README_CHECKER_PATH, fixture_with_markers("#!/usr/bin/env python3", REQUIRED_TESTS_CHECKER_MARKERS))
    write_text(root / ROLLBACK_THRESHOLD_CHECKER_PATH, fixture_with_markers("#!/usr/bin/env python3", REQUIRED_ROLLBACK_CHECKER_MARKERS))
    write_text(root / RCU_GUARDRAIL_CHECKER_PATH, fixture_with_markers("#!/usr/bin/env python3", REQUIRED_RCU_GUARDRAIL_MARKERS))
    write_text(root / RELEASE_BOUNDARY_CHECKER_PATH, fixture_with_markers("#!/usr/bin/env python3", REQUIRED_RELEASE_CHECKER_MARKERS))
    write_text(root / VALIDATOR_PATH, fixture_with_markers("#!/usr/bin/env python3", REQUIRED_VALIDATOR_MARKERS))
    write_text(
        root / MAKEFILE_PATH,
        "phase14-validate:\n"
        "\tpython3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test\n"
        "\tpython3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py\n"
        "\tpython3 scripts/zigux/validate-phase14.py --self-test\n"
        "\tpython3 scripts/zigux/validate-phase14.py\n",
    )


def remove_once(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    updated = content.replace(f"- {text}\n", "", 1)
    if updated == content:
        updated = content.replace(text + "\n", "", 1)
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = check(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-productization-gap-"))
    try:
        write_fixture_tree(base)
        failures = check(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = [
            PRODUCTIZATION_GAP_PATH,
            DOCS_README_PATH,
            TESTS_README_PATH,
            TESTS_README_CHECKER_PATH,
            VALIDATOR_PATH,
        ]
        for rel in missing_file_cases:
            write_fixture_tree(base)
            (base / rel).unlink()
            expect_failure(base, f"missing_file:{rel.as_posix()}")

        marker_cases = [
            (PRODUCTIZATION_GAP_PATH, REQUIRED_PRODUCTIZATION_MARKERS[5]),
            (PRODUCTIZATION_GAP_PATH, REQUIRED_PRODUCTIZATION_MARKERS[10]),
            (DOCS_README_PATH, REQUIRED_DOCS_README_MARKERS[1]),
            (REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_MARKERS[2]),
            (TESTS_README_PATH, REQUIRED_TESTS_SECTION_MARKERS[0]),
            (SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS[2]),
            (TESTS_README_CHECKER_PATH, REQUIRED_TESTS_CHECKER_MARKERS[2]),
            (VALIDATOR_PATH, REQUIRED_VALIDATOR_MARKERS[1]),
        ]
        for rel, marker in marker_cases:
            write_fixture_tree(base)
            remove_once(base / rel, marker)
            expect_failure(base, f"missing_marker:{rel.as_posix()}:{marker}")

        forbidden_case = FORBIDDEN_MAKEFILE_MARKERS[0]
        write_fixture_tree(base)
        with (base / MAKEFILE_PATH).open("a", encoding="utf-8") as handle:
            handle.write(forbidden_case + "\n")
        expect_failure(base, f"forbidden_marker:{MAKEFILE_PATH.as_posix()}:{forbidden_case}")

        case_count = len(missing_file_cases) + len(marker_cases) + 1
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST=pass")
        print(f"PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the bounded Phase 14 productization-gap survey stays aligned "
            "with the current docs-root, tests-root, checklist, route-checker, and "
            "single-gate `phase14-validate` posture."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = check(args.root)
    if failures:
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY=fail")
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_PRODUCTIZATION_GAP_SURVEY_DRIFT_END")
        return 1

    print("PHASE14_PRODUCTIZATION_GAP_SURVEY=pass")
    print(f"PHASE14_PRODUCTIZATION_GAP_SURVEY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE14_PRODUCTIZATION_GAP_SURVEY_REQUIRED_MARKER_COUNT="
        f"{sum(len(group) for group in [REQUIRED_PRODUCTIZATION_MARKERS, REQUIRED_DOCS_README_MARKERS, REQUIRED_REVIEW_CHECKLIST_MARKERS, REQUIRED_TESTS_SECTION_MARKERS, REQUIRED_SCRIPTS_README_MARKERS, REQUIRED_TESTS_CHECKER_MARKERS, REQUIRED_ROLLBACK_CHECKER_MARKERS, REQUIRED_RCU_GUARDRAIL_MARKERS, REQUIRED_RELEASE_CHECKER_MARKERS, REQUIRED_VALIDATOR_MARKERS, REQUIRED_MAKEFILE_MARKERS])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
