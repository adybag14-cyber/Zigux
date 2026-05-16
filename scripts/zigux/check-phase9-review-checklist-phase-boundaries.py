#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/review-checklist.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
TESTS_README_PATH = "zigux/tests/README.md"

PHASE9_SHARED_PACKET_MARKER = "if the change touches the shared Phase 9 runtime-loader packet"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"
LANE_SEQUENCING_SAMPLE_MARKER = "surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`"
LANE_SEQUENCING_SELFTEST_MARKER = "`.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking"
LANE_SEQUENCING_BACKLOG_MARKER = "does not currently expose the broader shared runtime-loader packet"
TESTS_README_TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
TESTS_README_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
TESTS_README_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"

CHECKLIST_REQUIRED_MARKERS = [
    PHASE9_SHARED_PACKET_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    LANE_SEQUENCING_SAMPLE_MARKER,
    LANE_SEQUENCING_SELFTEST_MARKER,
    LANE_SEQUENCING_BACKLOG_MARKER,
]

TESTS_README_REQUIRED_MARKERS = [
    TESTS_README_TRACE_EVENTS_SAMPLE_MARKER,
    TESTS_README_SELFTEST_HOOK_MARKER,
    TESTS_README_LIFECYCLE_MARKER,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    checklist_path = root / REVIEW_CHECKLIST_PATH
    lane_sequencing_path = root / LANE_SEQUENCING_PATH
    tests_readme_path = root / TESTS_README_PATH
    if not checklist_path.exists():
        failures.append(f"missing_file:{REVIEW_CHECKLIST_PATH}")
    if not lane_sequencing_path.exists():
        failures.append(f"missing_file:{LANE_SEQUENCING_PATH}")
    if not tests_readme_path.exists():
        failures.append(f"missing_file:{TESTS_README_PATH}")
    if failures:
        return failures

    checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    for marker in CHECKLIST_REQUIRED_MARKERS:
        if marker not in checklist:
            failures.append(f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")

    lane_sequencing = read_text(root, LANE_SEQUENCING_PATH)
    for marker in LANE_SEQUENCING_REQUIRED_MARKERS:
        if marker not in lane_sequencing:
            failures.append(f"missing_marker:{LANE_SEQUENCING_PATH}:{marker}")

    tests_readme = read_text(root, TESTS_README_PATH)
    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme:
            failures.append(f"missing_marker:{TESTS_README_PATH}:{marker}")

    return failures


def build_fixture_text() -> str:
    return f"""# Zigux Review Checklist

- {PHASE9_SHARED_PACKET_MARKER}
- the shared Phase 9 reminder should also keep the older cross-phase non-owner boundaries explicit:
  {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {PHASE2_BOUNDARY_MARKER}, while
  {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {PHASE3_BOUNDARY_MARKER}.
"""


def build_lane_sequencing_fixture_text() -> str:
    return f"""# Phase 9 Runtime Pilot Lane Sequencing

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving runtime-module evidence inside that sample: {LANE_SEQUENCING_SELFTEST_MARKER}

Current `master` {LANE_SEQUENCING_BACKLOG_MARKER} that earlier reminder surfaces described.
"""


def build_tests_readme_fixture_text() -> str:
    return f"""# zigux/tests

Phase 9 review packet
  * the surviving trace-events sample still keeps the roadmap-backed runtime pilot shape concrete by exposing {TESTS_README_SELFTEST_HOOK_MARKER} together with {TESTS_README_LIFECYCLE_MARKER} inside {TESTS_README_TRACE_EVENTS_SAMPLE_MARKER}, so reviewers can still inspect one real runtime-module and selftest-hook surface while the broader shared loader packet remains backlog
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        fixture_path = base / REVIEW_CHECKLIST_PATH
        lane_sequencing_path = base / LANE_SEQUENCING_PATH
        tests_readme_path = base / TESTS_README_PATH
        write_text(fixture_path, build_fixture_text())
        write_text(lane_sequencing_path, build_lane_sequencing_fixture_text())
        write_text(tests_readme_path, build_tests_readme_fixture_text())
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in CHECKLIST_REQUIRED_MARKERS:
            write_text(fixture_path, build_fixture_text().replace(marker, "", 1))
            write_text(lane_sequencing_path, build_lane_sequencing_fixture_text())
            write_text(tests_readme_path, build_tests_readme_fixture_text())
            expect_failure(base, f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")
            write_text(fixture_path, build_fixture_text())

        for marker in LANE_SEQUENCING_REQUIRED_MARKERS:
            write_text(fixture_path, build_fixture_text())
            write_text(lane_sequencing_path, build_lane_sequencing_fixture_text().replace(marker, "", 1))
            write_text(tests_readme_path, build_tests_readme_fixture_text())
            expect_failure(base, f"missing_marker:{LANE_SEQUENCING_PATH}:{marker}")
            write_text(lane_sequencing_path, build_lane_sequencing_fixture_text())

        for marker in TESTS_README_REQUIRED_MARKERS:
            write_text(fixture_path, build_fixture_text())
            write_text(lane_sequencing_path, build_lane_sequencing_fixture_text())
            write_text(tests_readme_path, build_tests_readme_fixture_text().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{TESTS_README_PATH}:{marker}")
            write_text(tests_readme_path, build_tests_readme_fixture_text())

        (base / REVIEW_CHECKLIST_PATH).unlink()
        expect_failure(base, f"missing_file:{REVIEW_CHECKLIST_PATH}")
        write_text(fixture_path, build_fixture_text())
        write_text(lane_sequencing_path, build_lane_sequencing_fixture_text())
        write_text(tests_readme_path, build_tests_readme_fixture_text())

        (base / LANE_SEQUENCING_PATH).unlink()
        expect_failure(base, f"missing_file:{LANE_SEQUENCING_PATH}")
        write_text(fixture_path, build_fixture_text())
        write_text(lane_sequencing_path, build_lane_sequencing_fixture_text())
        write_text(tests_readme_path, build_tests_readme_fixture_text())

        (base / TESTS_README_PATH).unlink()
        expect_failure(base, f"missing_file:{TESTS_README_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 9 review checklist keeps older Phase 2 and Phase 3 non-owner boundaries explicit, that the lane-sequencing note keeps the surviving trace-events packet explicit, and that the tests guide keeps the same selftest-hook lifecycle evidence visible."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_ERROR={failure}")
        return 1

    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
