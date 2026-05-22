#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


EXIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
REENTRY_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig"

EXIT_ROLLBACK_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {',
    "try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);",
    "try std.testing.expectEqual(@as(usize, 2), before_failed_exit.register_transitions);",
    "try std.testing.expectEqual(@as(usize, 1), before_failed_exit.unregister_transitions);",
    "try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_template_cond_message);",
    'try std.testing.expectEqualStrings("Hello __rel_loc", after_failed_exit_main_replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);',
    "try std.testing.expectEqual(@as(?usize, 4), before_unregister.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_unregister.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_unregister.last_main_conditional_event_count);",
    'try std.testing.expectEqualStrings("Look at me too", before_unregister.last_function_template_message orelse return error.ExpectedFunctionPayload);',
    "try std.testing.expectEqual(@as(usize, 1), before_exit.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);",
    "try std.testing.expectEqual(@as(?usize, 0), before_exit.last_main_conditional_event_count);",
    "try std.testing.expectEqual(@as(usize, 2), after_exit.unregister_transitions);",
    "try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);",
    "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
]

REENTRY_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest" {',
    "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_exit.last_main_conditional_event_count);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_template_cond_message);",
    'try std.testing.expectEqualStrings("Hello __rel_loc", before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("iter=%d", before_exit.last_format_template orelse return error.ExpectedMainPayload);',
    "try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);",
    "try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqual(before_exit.last_main_conditional_message, after_exit.last_main_conditional_message);",
    "try std.testing.expectEqual(before_exit.last_main_template_cond_message, after_exit.last_main_template_cond_message);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(11));",
    "try std.testing.expect(std.meta.eql(after_exit, after_rejected_lifecycle));",
]

FILE_MARKERS = {
    EXIT_ROLLBACK_GUARD_SAMPLE_PATH: EXIT_ROLLBACK_REQUIRED_MARKERS,
    REENTRY_GATE_SAMPLE_PATH: REENTRY_REQUIRED_MARKERS,
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
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-summary-preservation-"))
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

        print("PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_SELF_TEST=pass")
        print(
            "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_EXIT_MARKER_COUNT="
            f"{len(FILE_MARKERS[EXIT_ROLLBACK_GUARD_SAMPLE_PATH])}"
        )
        print(
            "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_REENTRY_MARKER_COUNT="
            f"{len(FILE_MARKERS[REENTRY_GATE_SAMPLE_PATH])}"
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

    print("PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION=pass")
    print(
        "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_EXIT_MARKER_COUNT="
        f"{len(FILE_MARKERS[EXIT_ROLLBACK_GUARD_SAMPLE_PATH])}"
    )
    print(
        "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_REENTRY_MARKER_COUNT="
        f"{len(FILE_MARKERS[REENTRY_GATE_SAMPLE_PATH])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
