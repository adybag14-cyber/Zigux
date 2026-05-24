#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SAMPLE_PATH = "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig"

REQUIRED_MARKERS = {
    SURVEY_NOTE_PATH: [
        "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
        "The reinit/reexit companion still keeps rejected re-init and rejected re-exit rollback explicit after both initialized direct activity and selftest-ready replay, so the same narrow packet now spells out that lifecycle retries fail closed without mutating the captured summaries.",
    ],
    PHASE9_BUILD_PATH: [
        '.name = "phase9-runtime-trace-events-reinit-reexit-guard-tests"',
        '../../samples/zigux/runtime_trace_events_reinit_reexit_guard.zig',
        'phase9_runtime_trace_events.dependOn(\n        &run_runtime_trace_events_reinit_reexit_guard_tests.step,\n    );',
    ],
    WORKFLOW_PATH: [
        "zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    ],
    SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay" {',
        'test "phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay" {',
        "try expectSummaryStable(before_initialized_reinit, initialized_module.summary());",
        "try expectSummaryStable(before_selftested_reinit, selftested_module.summary());",
        "try expectSummaryStable(before_exited_reinit, exited_module.summary());",
        "try expectSummaryStable(before_initialized_reexit, initialized_module.summary());",
        "try expectSummaryStable(before_selftested_reexit, selftested_module.summary());",
    ],
}

EXACT_ONCE_MARKERS = {
    SURVEY_NOTE_PATH: [
        "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    ],
    PHASE9_BUILD_PATH: [
        '.name = "phase9-runtime-trace-events-reinit-reexit-guard-tests"',
    ],
    WORKFLOW_PATH: [
        "zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    ],
    SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay" {',
        'test "phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay" {',
    ],
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SURVEY_NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


def break_marker(marker: str) -> str:
    if len(marker) == 1:
        return "_"
    replacement_tail = "_" if marker[-1] != "_" else "-"
    return marker[:-1] + replacement_tail


def tamper_marker_occurrences(content: str, marker: str) -> str:
    return content.replace(marker, break_marker(marker))


def build_fixture_text(rel_path: str) -> str:
    markers = REQUIRED_MARKERS[rel_path]
    prefix = "# fixture\n\n" if rel_path.endswith(".md") else ""
    return prefix + "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in EXACT_ONCE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            count = count_exact_line_occurrences(text, marker)
            if count != 1:
                failures.append(f"expected_exact_once:{rel_path}:{marker}:count={count}")

    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path in REQUIRED_MARKERS:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-reinit-reexit-guard-route-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, tamper_marker_occurrences(current, marker))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path, markers in EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

        for rel_path in REQUIRED_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_SELF_TEST=pass")
    print(f"PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_ERROR={failure}")
        return 1

    print(f"PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_TRACE_EVENTS_REINIT_REEXIT_GUARD_ROUTE_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())