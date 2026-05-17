#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"
UNREGISTERED_GATE_PATH = "samples/zigux/runtime_trace_events_unregistered_gate.zig"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / MODULE_SLICE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

MODULE_SLICE_HEADER_MARKER = "# Phase 9 Runtime Trace-Events Module Slice"
MODULE_SLICE_PACKET_MARKER = "Current `master` keeps only a narrow direct trace-events runtime packet in this family-local slice:"
MODULE_SLICE_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
MODULE_SLICE_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
MODULE_SLICE_LANE_NOTE_MARKER = "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`"
MODULE_SLICE_CHECKER_MARKER = "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
MODULE_SLICE_SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
MODULE_SLICE_LIFECYCLE_MARKER = "initialized, selftest_complete, and exited sample-local lifecycle tracking"
MODULE_SLICE_SAMPLE_LOCAL_ONLY_MARKER = (
    "do not by themselves prove live `module_init()`, `module_exit()`, depmod-visible module registration, or the removed shared runtime-loader substrate on current `master`"
)
MODULE_SLICE_INIT_MARKER = (
    "`init()` only accepts the `.cold` stage, resets registration depth, counters, labels, and cached payloads, increments `init_runs`, and moves `stage_state` to `.initialized`."
)
MODULE_SLICE_REGISTER_MARKER = (
    "`registerFunctionThread()` only runs through `ensureMutable()` while the sample is still `.initialized` or `.selftest_complete`; if `registration_depth != 0` it returns `error.FunctionThreadAlreadyRegistered`, otherwise it sets `registration_depth = 1` and `last_register_label = \"foo_bar_reg\"`."
)
MODULE_SLICE_EMIT_FN_MARKER = "`emitFunctionIteration()` rejects use without prior registration with `error.FunctionThreadNotRegistered`."
MODULE_SLICE_SELFTEST_MARKER = (
    "`runSelftest()` is only accepted from `.initialized`; it replays `emitMainIteration(0)`, `registerFunctionThread()`, `emitFunctionIteration(1)`, and `unregisterFunctionThread()` before incrementing `selftest_runs` and moving the sample to `.selftest_complete`."
)
MODULE_SLICE_EXIT_MARKER = (
    "`unregisterFunctionThread()` fails closed with `error.RegistrationUnderflow` when the depth is already zero, and `exit()` rejects nonzero registration depth with `error.OutstandingRegistration` before allowing the `.exited` stage."
)
MODULE_SLICE_DUPLICATE_REGISTRATION_MARKER = (
    "The shipped duplicate-registration test in `samples/zigux/runtime_trace_events.zig` confirms that a second `registerFunctionThread()` call preserves the prior summary and fails with `error.FunctionThreadAlreadyRegistered`."
)
MODULE_SLICE_ABSENT_LOADER_MARKER = "does not currently expose the broader shared runtime-loader packet"
MODULE_SLICE_BACKLOG_MARKER = (
    "No current family-local trace-events packet should therefore describe `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_module.zig`, `zigux/tests/runtime_trace_events_diff.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `zigux/tests/runtime_trace_events_survey.zig`, or `zigux/tests/runtime_trace_events_manifest.json` as shipped current-`master` evidence unless a fresh repo reread proves they have returned."
)

SAMPLE_DESCRIPTOR_MARKER = '.provides_selftest_hook = true'
SAMPLE_RUN_SELFTEST_MARKER = "pub fn runSelftest(self: *Self) !EmissionSummary {"
SAMPLE_REGISTER_MARKER = "pub fn registerFunctionThread(self: *Self) !void {"
SAMPLE_UNREGISTER_MARKER = "pub fn unregisterFunctionThread(self: *Self) !void {"
SAMPLE_EXIT_MARKER = "pub fn exit(self: *Self) !void {"
SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER = (
    'test "trace-events sample rejects duplicate function-thread registration" {'
)
SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER = "error.FunctionThreadAlreadyRegistered"
SAMPLE_OUTSTANDING_REGISTRATION_MARKER = "error.OutstandingRegistration"

UNREGISTERED_GATE_TEST_MARKER = (
    'test "phase9 trace-events sample keeps unregistered function-thread failures fail-closed" {'
)
UNREGISTERED_GATE_FN_REJECTION_MARKER = "error.FunctionThreadNotRegistered"
UNREGISTERED_GATE_UNREGISTER_REJECTION_MARKER = "error.RegistrationUnderflow"
UNREGISTERED_GATE_SELFTEST_STAGE_MARKER = "ModuleStage.selftest_complete"

MODULE_SLICE_REQUIRED_MARKERS = [
    MODULE_SLICE_HEADER_MARKER,
    MODULE_SLICE_PACKET_MARKER,
    MODULE_SLICE_GATE_MARKER,
    MODULE_SLICE_LANE_NOTE_MARKER,
    MODULE_SLICE_CHECKER_MARKER,
    MODULE_SLICE_SELFTEST_HOOK_MARKER,
    MODULE_SLICE_LIFECYCLE_MARKER,
    MODULE_SLICE_SAMPLE_LOCAL_ONLY_MARKER,
    MODULE_SLICE_INIT_MARKER,
    MODULE_SLICE_REGISTER_MARKER,
    MODULE_SLICE_EMIT_FN_MARKER,
    MODULE_SLICE_SELFTEST_MARKER,
    MODULE_SLICE_EXIT_MARKER,
    MODULE_SLICE_DUPLICATE_REGISTRATION_MARKER,
    MODULE_SLICE_ABSENT_LOADER_MARKER,
    MODULE_SLICE_BACKLOG_MARKER,
]

SAMPLE_REQUIRED_MARKERS = [
    SAMPLE_DESCRIPTOR_MARKER,
    SAMPLE_RUN_SELFTEST_MARKER,
    SAMPLE_REGISTER_MARKER,
    SAMPLE_UNREGISTER_MARKER,
    SAMPLE_EXIT_MARKER,
    SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER,
    SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER,
    SAMPLE_OUTSTANDING_REGISTRATION_MARKER,
]

UNREGISTERED_GATE_REQUIRED_MARKERS = [
    UNREGISTERED_GATE_TEST_MARKER,
    UNREGISTERED_GATE_FN_REJECTION_MARKER,
    UNREGISTERED_GATE_UNREGISTER_REJECTION_MARKER,
    UNREGISTERED_GATE_SELFTEST_STAGE_MARKER,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required = [
        MODULE_SLICE_PATH,
        SAMPLE_PATH,
        UNREGISTERED_GATE_PATH,
    ]
    for rel_path in required:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in [
        (MODULE_SLICE_PATH, MODULE_SLICE_REQUIRED_MARKERS),
        (SAMPLE_PATH, SAMPLE_REQUIRED_MARKERS),
        (UNREGISTERED_GATE_PATH, UNREGISTERED_GATE_REQUIRED_MARKERS),
    ]:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_module_slice_fixture_text() -> str:
    return f"""# Phase 9 Runtime Trace-Events Module Slice

Current `master` keeps only a narrow direct trace-events runtime packet in this family-local slice:
  * `samples/zigux/runtime_trace_events.zig`
  * `samples/zigux/runtime_trace_events_unregistered_gate.zig`
  * `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  * `scripts/zigux/check-phase9-trace-events-runtime-packet.py`

The direct sample keeps the roadmap-facing pilot contract concrete through `RuntimeTraceEventsSample.descriptor()` and `.provides_selftest_hook = true`, together with initialized, selftest_complete, and exited sample-local lifecycle tracking.
Those cues remain reviewable pilot-module evidence only; they do not by themselves prove live `module_init()`, `module_exit()`, depmod-visible module registration, or the removed shared runtime-loader substrate on current `master`.

`init()` only accepts the `.cold` stage, resets registration depth, counters, labels, and cached payloads, increments `init_runs`, and moves `stage_state` to `.initialized`.
`registerFunctionThread()` only runs through `ensureMutable()` while the sample is still `.initialized` or `.selftest_complete`; if `registration_depth != 0` it returns `error.FunctionThreadAlreadyRegistered`, otherwise it sets `registration_depth = 1` and `last_register_label = "foo_bar_reg"`.
`emitFunctionIteration()` rejects use without prior registration with `error.FunctionThreadNotRegistered`.
`runSelftest()` is only accepted from `.initialized`; it replays `emitMainIteration(0)`, `registerFunctionThread()`, `emitFunctionIteration(1)`, and `unregisterFunctionThread()` before incrementing `selftest_runs` and moving the sample to `.selftest_complete`.
`unregisterFunctionThread()` fails closed with `error.RegistrationUnderflow` when the depth is already zero, and `exit()` rejects nonzero registration depth with `error.OutstandingRegistration` before allowing the `.exited` stage.
The shipped duplicate-registration test in `samples/zigux/runtime_trace_events.zig` confirms that a second `registerFunctionThread()` call preserves the prior summary and fails with `error.FunctionThreadAlreadyRegistered`.

Current `master` does not currently expose the broader shared runtime-loader packet that older Phase 9 reminder surfaces described.
No current family-local trace-events packet should therefore describe `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_module.zig`, `zigux/tests/runtime_trace_events_diff.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `zigux/tests/runtime_trace_events_survey.zig`, or `zigux/tests/runtime_trace_events_manifest.json` as shipped current-`master` evidence unless a fresh repo reread proves they have returned.
"""


def build_sample_fixture_text() -> str:
    return """pub fn registerFunctionThread(self: *Self) !void {}
pub fn unregisterFunctionThread(self: *Self) !void {}
pub fn runSelftest(self: *Self) !EmissionSummary {}
pub fn exit(self: *Self) !void {}

pub fn descriptor() ModuleDescriptor {
    return .{
        .provides_selftest_hook = true,
    };
}

test \"trace-events sample rejects duplicate function-thread registration\" {
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
}

fn failedExit() void {
    _ = error.OutstandingRegistration;
}
"""


def build_unregistered_gate_fixture_text() -> str:
    return """test \"phase9 trace-events sample keeps unregistered function-thread failures fail-closed\" {
    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(3));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_before.stage);
}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-runtime-trace-events-module-slice-"))
    try:
        write_text(base / MODULE_SLICE_PATH, build_module_slice_fixture_text())
        write_text(base / SAMPLE_PATH, build_sample_fixture_text())
        write_text(base / UNREGISTERED_GATE_PATH, build_unregistered_gate_fixture_text())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, builder, markers in [
            (MODULE_SLICE_PATH, build_module_slice_fixture_text, MODULE_SLICE_REQUIRED_MARKERS),
            (SAMPLE_PATH, build_sample_fixture_text, SAMPLE_REQUIRED_MARKERS),
            (UNREGISTERED_GATE_PATH, build_unregistered_gate_fixture_text, UNREGISTERED_GATE_REQUIRED_MARKERS),
        ]:
            for marker in markers:
                write_text(base / MODULE_SLICE_PATH, build_module_slice_fixture_text())
                write_text(base / SAMPLE_PATH, build_sample_fixture_text())
                write_text(base / UNREGISTERED_GATE_PATH, build_unregistered_gate_fixture_text())
                write_text(base / rel_path, builder().replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in [
            MODULE_SLICE_PATH,
            SAMPLE_PATH,
            UNREGISTERED_GATE_PATH,
        ]:
            write_text(base / MODULE_SLICE_PATH, build_module_slice_fixture_text())
            write_text(base / SAMPLE_PATH, build_sample_fixture_text())
            write_text(base / UNREGISTERED_GATE_PATH, build_unregistered_gate_fixture_text())
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_RUNTIME_TRACE_EVENTS_MODULE_SLICE_SELF_TEST=pass")
        print(f"PHASE9_RUNTIME_TRACE_EVENTS_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
        print(f"PHASE9_RUNTIME_TRACE_EVENTS_MODULE_SAMPLE_MARKER_COUNT={len(SAMPLE_REQUIRED_MARKERS)}")
        print(f"PHASE9_RUNTIME_TRACE_EVENTS_MODULE_GATE_MARKER_COUNT={len(UNREGISTERED_GATE_REQUIRED_MARKERS)}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
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

    print("PHASE9_RUNTIME_TRACE_EVENTS_MODULE_SLICE=pass")
    print(f"PHASE9_RUNTIME_TRACE_EVENTS_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_TRACE_EVENTS_MODULE_SAMPLE_MARKER_COUNT={len(SAMPLE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_TRACE_EVENTS_MODULE_GATE_MARKER_COUNT={len(UNREGISTERED_GATE_REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
