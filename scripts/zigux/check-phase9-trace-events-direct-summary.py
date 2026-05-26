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
    "try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);",
    "try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);",
    'test "selftest path still records both conditional families at count zero" {',
    "try std.testing.expectEqual(@as(?usize, 6), replay.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), replay.last_main_conditional_event_count);",
    'try std.testing.expectEqualStrings("Some times print", replay.last_main_conditional_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("prints other times", replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);',
    'test "trace-events sample keeps conditional replay explicit after selftest" {',
    'try std.testing.expectEqualStrings("Some times print", before_conditional_replay.last_main_conditional_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("prints other times", before_conditional_replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("event-sample", after_conditional_replay.main_thread_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings("event-sample-fn", after_conditional_replay.function_thread_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings("foo_bar_reg", after_conditional_replay.last_register_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings("foo_bar_unreg", after_conditional_replay.last_unregister_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings("hello", after_conditional_replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("Mother Goose", after_conditional_replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);',
    "try std.testing.expectEqual(@as(usize, 0), after_conditional_replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);",
    "try std.testing.expect(after_conditional_replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);",
    'try std.testing.expectEqualStrings("HELLO", after_conditional_replay.last_main_template_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("Some times print", after_conditional_replay.last_main_conditional_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("prints other times", after_conditional_replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("I have to be different", after_conditional_replay.last_main_template_print_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("Hello __rel_loc", after_conditional_replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("iter=%d", after_conditional_replay.last_format_template orelse return error.ExpectedMainPayload);',
    'test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {',
    "try std.testing.expectEqual(ModuleStage.initialized, initialized_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_summary.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_summary.register_transitions);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_summary.unregister_transitions);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.register_transitions);",
    "try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.unregister_transitions);",
    "try std.testing.expectEqual(@as(?usize, 4), selftest_complete_summary.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), selftest_complete_summary.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), selftest_complete_summary.last_main_conditional_event_count);",
    'try std.testing.expectEqualStrings("Frodo", selftest_complete_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);',
    'try std.testing.expectEqualStrings("Look at me", selftest_complete_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings("Look at me too", selftest_complete_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);',
    "try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);",
    'try std.testing.expectEqualStrings(selftest_complete_summary.last_register_label orelse return error.ExpectedFunctionPayload, exited_summary.last_register_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings(selftest_complete_summary.last_unregister_label orelse return error.ExpectedFunctionPayload, exited_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);',
    'test "trace-events sample preserves initialized summary across direct exit without selftest" {',
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, null), before_exit.last_main_conditional_event_count);",
    'test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {',
    "try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);",
    'test "trace-events sample keeps rejected re-selftest rollback explicit" {',
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);",
    'try std.testing.expectEqualStrings("foo_bar_reg", before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings("foo_bar_unreg", before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings(before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings(before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);',
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.register_transitions);",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.unregister_transitions);",
    'try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload);',
    'try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);',
    "try std.testing.expectEqual(before_rejected_exit_selftest.last_main_conditional_event_count, after_rejected_exit_selftest.last_main_conditional_event_count);",
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