#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


DIRECT_SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"

DIRECT_SAMPLE_REQUIRED_MARKERS = [
    "last_main_emitted_events: ?usize,",
    "last_fn_emitted_events: ?usize,",
    "last_main_conditional_event_count: ?usize,",
    'test "count-gated main-thread replay matches the Linux sample conditions" {',
    "try std.testing.expectEqual(@as(?usize, 4), replay.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), replay.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), replay.last_main_conditional_event_count);",
    'test "selftest path still records both conditional families at count zero" {',
    "try std.testing.expectEqual(@as(?usize, 6), replay.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), replay.last_main_conditional_event_count);",
    'test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {',
    "try std.testing.expectEqual(@as(?usize, 4), selftest_complete_summary.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), selftest_complete_summary.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), selftest_complete_summary.last_main_conditional_event_count);",
    'test "trace-events sample preserves initialized summary across direct exit without selftest" {',
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_conditional_event_count);",
    'test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {',
    "try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);",
]


FILE_MARKERS = {
    DIRECT_SAMPLE_PATH: DIRECT_SAMPLE_REQUIRED_MARKERS,
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text(markers: list[str]) -> str:
    return "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers in FILE_MARKERS.items():
        candidate = root / rel_path
        if not candidate.exists():
            failures.append(f"missing_file:{rel_path}")
            continue
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        write_text(base / rel_path, build_fixture_text(markers))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-direct-summary-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_SELF_TEST=pass")
        print(
            "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_MARKER_COUNT="
            f"{len(FILE_MARKERS[DIRECT_SAMPLE_PATH])}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_TRACE_EVENTS_DIRECT_SUMMARY=pass")
    print(
        "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_MARKER_COUNT="
        f"{len(FILE_MARKERS[DIRECT_SAMPLE_PATH])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
