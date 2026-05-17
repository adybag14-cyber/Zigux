#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
TESTS_README_PATH = "zigux/tests/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
TRACE_EVENTS_PACKET_CHECKER_MARKER = "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
ABSENT_SHARED_LOADER_MARKER = "does not currently expose the broader shared runtime-loader packet"
ABSENT_PHASE9_BUILD_MARKER = "`zigux/tests/phase9_build.zig`"
ABSENT_RUNTIME_LOADER_KERNEL_MARKER = "`zigux/kernel/runtime_loader.zig`"
ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER = "`samples/zigux/runtime_*_loader.zig` scaffolds"
ABSENT_WORKFLOW_MARKER = "`.github/workflows/zigux-bootstrap.yml`"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"

TESTS_README_BACKLOG_MARKER = (
    "there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, "
    "`make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`"
)

SAMPLE_DESCRIPTOR_MARKER = ".provides_selftest_hook = true"
SAMPLE_RUN_SELFTEST_MARKER = "pub fn runSelftest(self: *Self) !EmissionSummary {"
SAMPLE_EXIT_MARKER = "pub fn exit(self: *Self) !void {"
SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER = (
    'test "trace-events sample rejects duplicate function-thread registration" {'
)
SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER = "error.FunctionThreadAlreadyRegistered"
SAMPLE_CONTINUITY_TEST_MARKER = (
    'test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {'
)
SAMPLE_COLD_STAGE_MARKER = "try std.testing.expectEqual(ModuleStage.cold, module.stage());"
SAMPLE_COLD_SELFTEST_REJECTION_MARKER = (
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());"
)
SAMPLE_COLD_EXIT_REJECTION_MARKER = (
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());"
)
SAMPLE_FAILED_EXIT_TEST_MARKER = (
    'test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {'
)
SAMPLE_REJECTED_SELFTEST_TEST_MARKER = (
    'test "trace-events sample keeps rejected re-selftest rollback explicit" {'
)
SAMPLE_EXITED_MAIN_REPLAY_REJECTION_MARKER = (
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(13));"
)
SAMPLE_EXITED_REGISTRATION_REJECTION_MARKER = (
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());"
)
SAMPLE_EXITED_FN_REPLAY_REJECTION_MARKER = (
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(15));"
)
SAMPLE_EXITED_UNREGISTER_REJECTION_MARKER = (
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());"
)
SAMPLE_EXITED_STAGE_MARKER = "try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);"
SAMPLE_EXIT_RUN_COUNT_MARKER = "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);"
SAMPLE_OUTSTANDING_REGISTRATION_MARKER = "error.OutstandingRegistration"

SEQUENCING_REQUIRED_MARKERS = [
    TRACE_EVENTS_SAMPLE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
    ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
    ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER,
]

TESTS_README_REQUIRED_MARKERS = [
    TRACE_EVENTS_SAMPLE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    TESTS_README_BACKLOG_MARKER,
]

SAMPLES_README_REQUIRED_MARKERS = [
    TRACE_EVENTS_SAMPLE_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
    ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
    ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER,
    ABSENT_WORKFLOW_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
]

SAMPLE_REQUIRED_MARKERS = [
    SAMPLE_DESCRIPTOR_MARKER,
    SAMPLE_RUN_SELFTEST_MARKER,
    SAMPLE_EXIT_MARKER,
    SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER,
    SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER,
    SAMPLE_CONTINUITY_TEST_MARKER,
    SAMPLE_COLD_STAGE_MARKER,
    SAMPLE_COLD_SELFTEST_REJECTION_MARKER,
    SAMPLE_COLD_EXIT_REJECTION_MARKER,
    SAMPLE_FAILED_EXIT_TEST_MARKER,
    SAMPLE_REJECTED_SELFTEST_TEST_MARKER,
    SAMPLE_EXITED_MAIN_REPLAY_REJECTION_MARKER,
    SAMPLE_EXITED_REGISTRATION_REJECTION_MARKER,
    SAMPLE_EXITED_FN_REPLAY_REJECTION_MARKER,
    SAMPLE_EXITED_UNREGISTER_REJECTION_MARKER,
    SAMPLE_EXITED_STAGE_MARKER,
    SAMPLE_EXIT_RUN_COUNT_MARKER,
    SAMPLE_OUTSTANDING_REGISTRATION_MARKER,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required = [SEQUENCING_PATH, TESTS_README_PATH, SAMPLES_README_PATH, SAMPLE_PATH]
    for rel_path in required:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in [
        (SEQUENCING_PATH, SEQUENCING_REQUIRED_MARKERS),
        (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
        (SAMPLES_README_PATH, SAMPLES_README_REQUIRED_MARKERS),
        (SAMPLE_PATH, SAMPLE_REQUIRED_MARKERS),
    ]:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_sequencing_fixture_text() -> str:
    return f"""# Phase 9 Runtime Pilot Lane Sequencing

Current `master` keeps a narrow surviving runtime-pilot packet.

- surviving direct runtime-module sample: {TRACE_EVENTS_SAMPLE_MARKER}
- surviving runtime-module evidence inside that sample: {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}

Current `master` {ABSENT_SHARED_LOADER_MARKER}.
Fresh repo-first rereads did not find {ABSENT_PHASE9_BUILD_MARKER}, the shared `zigux/tests/runtime_*` replay family, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, or the older {ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER} on `master`.
"""


def build_tests_readme_fixture_text() -> str:
    return f"""# zigux/tests

Phase 9 review packet
  * the surviving trace-events sample still keeps the roadmap-backed runtime pilot shape concrete by exposing {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER} inside {TRACE_EVENTS_SAMPLE_MARKER}, so reviewers can still inspect one real runtime-module and selftest-hook surface while the broader shared loader packet remains backlog
  * {TESTS_README_BACKLOG_MARKER}
"""


def build_samples_readme_fixture_text() -> str:
    return f"""# samples/zigux

## Separate Phase 9 runtime pilot family
* keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, {TRACE_EVENTS_PACKET_CHECKER_MARKER}, and `zigux/tests/README.md` aligned with the surviving direct runtime-module sample {TRACE_EVENTS_SAMPLE_MARKER}
* keep the current direct runtime-module evidence explicit: {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}
* keep saying clearly that current `master` {ABSENT_SHARED_LOADER_MARKER}, so {ABSENT_PHASE9_BUILD_MARKER}, the shared `zigux/tests/runtime_*` replay family, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, {ABSENT_WORKFLOW_MARKER}, and the older {ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER} stay backlog references unless a fresh repo reread proves they have returned
* keep older cross-phase non-owner boundaries explicit: {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} remain Phase 2 config-surface bridge references, while {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} remain Phase 3 export-boundary references rather than runtime-pilot evidence
"""


def build_sample_fixture_text() -> str:
    return f"""const std = @import(\"std\");

const Self = @This();
const ModuleStage = enum {{ cold, exited }};
const EmissionSummary = struct {{}};

pub const ModuleDescriptor = struct {{
    provides_selftest_hook: bool,
}};

pub fn descriptor() ModuleDescriptor {{
    return .{{ .provides_selftest_hook = true }};
}}

pub fn runSelftest(self: *Self) !EmissionSummary {{
    _ = self;
    return .{{}};
}}

pub fn exit(self: *Self) !void {{
    _ = self;
    return error.InvalidLifecycleTransition;
}}

test \"trace-events sample rejects duplicate function-thread registration\" {{
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
}}

test \"trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity\" {{
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(13));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(15));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
}}

test \"trace-events sample keeps failed-exit rollback explicit after selftest-ready replay\" {{
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
}}

test \"trace-events sample keeps rejected re-selftest rollback explicit\" {{
    try std.testing.expect(true);
}}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-runtime-packet-"))
    try:
        write_text(base / SEQUENCING_PATH, build_sequencing_fixture_text())
        write_text(base / TESTS_README_PATH, build_tests_readme_fixture_text())
        write_text(base / SAMPLES_README_PATH, build_samples_readme_fixture_text())
        write_text(base / SAMPLE_PATH, build_sample_fixture_text())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, builder, markers in [
            (SEQUENCING_PATH, build_sequencing_fixture_text, SEQUENCING_REQUIRED_MARKERS),
            (TESTS_README_PATH, build_tests_readme_fixture_text, TESTS_README_REQUIRED_MARKERS),
            (SAMPLES_README_PATH, build_samples_readme_fixture_text, SAMPLES_README_REQUIRED_MARKERS),
            (SAMPLE_PATH, build_sample_fixture_text, SAMPLE_REQUIRED_MARKERS),
        ]:
            for marker in markers:
                write_text(base / SEQUENCING_PATH, build_sequencing_fixture_text())
                write_text(base / TESTS_README_PATH, build_tests_readme_fixture_text())
                write_text(base / SAMPLES_README_PATH, build_samples_readme_fixture_text())
                write_text(base / SAMPLE_PATH, build_sample_fixture_text())
                write_text(base / rel_path, builder().replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in [SEQUENCING_PATH, TESTS_README_PATH, SAMPLES_README_PATH, SAMPLE_PATH]:
            write_text(base / SEQUENCING_PATH, build_sequencing_fixture_text())
            write_text(base / TESTS_README_PATH, build_tests_readme_fixture_text())
            write_text(base / SAMPLES_README_PATH, build_samples_readme_fixture_text())
            write_text(base / SAMPLE_PATH, build_sample_fixture_text())
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SEQUENCING_MARKER_COUNT={len(SEQUENCING_REQUIRED_MARKERS)}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLE_MARKER_COUNT={len(SAMPLE_REQUIRED_MARKERS)}")
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

    print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET=pass")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SEQUENCING_MARKER_COUNT={len(SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLE_MARKER_COUNT={len(SAMPLE_REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
