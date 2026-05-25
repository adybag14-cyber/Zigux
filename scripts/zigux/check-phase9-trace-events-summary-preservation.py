#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


EXIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
REENTRY_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig"
REINIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig"
REINIT_REEXIT_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig"

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
    'test "phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay" {',
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

REINIT_ROLLBACK_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample keeps re-init rollback explicit across initialized, selftest-complete, and exited states" {',
    "try std.testing.expectEqual(ModuleStage.initialized, before_initialized_reinit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.init_runs);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());",
    "try expectSummaryStable(before_initialized_reinit, after_initialized_reinit);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);",
    "try std.testing.expectEqual(@as(usize, 14), before_selftested_reinit.total_events);",
    'try std.testing.expectEqualStrings("Some times print", before_selftested_reinit.last_main_conditional_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("prints other times", before_selftested_reinit.last_main_template_cond_message orelse return error.ExpectedMainPayload);',
    "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());",
    "try expectSummaryStable(before_selftested_reinit, after_selftested_reinit);",
    "try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.exit_runs);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_template_cond_message);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());",
    "try expectSummaryStable(before_exited_reinit, after_exited_reinit);",
]

REINIT_REEXIT_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample keeps initialized direct-activity summary explicit across clean exit" {',
    "try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);",
    'try std.testing.expectEqualStrings("Mother Goose", before_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);',
    "try module.exit();",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
    'test "phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay" {',
    "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());",
    "try expectSummaryStable(before_initialized_reinit, initialized_module.summary());",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());",
    "try expectSummaryStable(before_selftested_reinit, selftested_module.summary());",
    "try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());",
    "try expectSummaryStable(before_exited_reinit, exited_module.summary());",
    'test "phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay" {',
    "try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());",
    "try expectSummaryStable(before_initialized_reexit, initialized_module.summary());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());",
    "try expectSummaryStable(before_selftested_reexit, selftested_module.summary());",
]

FILE_MARKERS = {
    EXIT_ROLLBACK_GUARD_SAMPLE_PATH: EXIT_ROLLBACK_REQUIRED_MARKERS,
    REENTRY_GATE_SAMPLE_PATH: REENTRY_REQUIRED_MARKERS,
    REINIT_ROLLBACK_GUARD_SAMPLE_PATH: REINIT_ROLLBACK_REQUIRED_MARKERS,
    REINIT_REEXIT_GUARD_SAMPLE_PATH: REINIT_REEXIT_REQUIRED_MARKERS,
}


FILE_EXACT_ONCE_MARKERS = {
    EXIT_ROLLBACK_GUARD_SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps initialized direct-activity exit rollback explicit before selftest replay" {',
    ],
    REENTRY_GATE_SAMPLE_PATH: [
        'test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest" {',
    ],
    REINIT_ROLLBACK_GUARD_SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps re-init rollback explicit across initialized, selftest-complete, and exited states" {',
    ],
    REINIT_REEXIT_GUARD_SAMPLE_PATH: [
        'test "phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay" {',
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text(markers: list[str]) -> str:
    return "\n".join(markers) + "\n"


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


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

    for rel_path, markers in FILE_EXACT_ONCE_MARKERS.items():
        if not (root / rel_path).exists():
            continue
        text = read_text(root, rel_path)
        for marker in markers:
            count = count_exact_line_occurrences(text, marker)
            if count != 1:
                failures.append(f"expected_exact_once:{rel_path}:{marker}:count={count}")
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

        for rel_path, markers in FILE_EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

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
        print(
            "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_REINIT_MARKER_COUNT="
            f"{len(FILE_MARKERS[REINIT_ROLLBACK_GUARD_SAMPLE_PATH])}"
        )
        print(
            "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_REINIT_REEXIT_MARKER_COUNT="
            f"{len(FILE_MARKERS[REINIT_REEXIT_GUARD_SAMPLE_PATH])}"
        )
        print(
            "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_EXACT_ONCE_MARKER_COUNT="
            f"{sum(len(markers) for markers in FILE_EXACT_ONCE_MARKERS.values())}"
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
    print(
        "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_REINIT_MARKER_COUNT="
        f"{len(FILE_MARKERS[REINIT_ROLLBACK_GUARD_SAMPLE_PATH])}"
    )
    print(
        "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_REINIT_REEXIT_MARKER_COUNT="
        f"{len(FILE_MARKERS[REINIT_REEXIT_GUARD_SAMPLE_PATH])}"
    )
    print(
        "PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_EXACT_ONCE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
