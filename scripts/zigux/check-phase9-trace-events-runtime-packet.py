#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
MANIFEST_PATH = "zigux/tests/runtime_trace_events_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/runtime_trace_events_survey.zig"
SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"
UNREGISTERED_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_unregistered_gate.zig"
REENTRY_GATE_SAMPLE_PATH = "samples/zigux/runtime_trace_events_registration_reentry_gate.zig"
EXIT_ROLLBACK_GUARD_SAMPLE_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
UNREGISTERED_GATE_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
REENTRY_GATE_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
EXIT_ROLLBACK_GUARD_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`"
TRACE_EVENTS_PACKET_CHECKER_MARKER = "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
FAIL_CLOSED_COMPANION_MARKER = "unregistered function-thread failures fail-closed"
REENTRY_COMPANION_MARKER = "balanced function-thread registration reusable before and after selftest"
EXIT_ROLLBACK_COMPANION_MARKER = "failed-exit rollback explicit after reusable selftest replay"
ABSENT_SHARED_LOADER_MARKER = "does not currently expose the broader shared runtime-loader packet"
ABSENT_PHASE9_BUILD_MARKER = "`zigux/tests/phase9_build.zig`"
ABSENT_RUNTIME_LOADER_KERNEL_MARKER = "`zigux/kernel/runtime_loader.zig`"
ABSENT_RUNTIME_LOADER_CONTRACT_MARKER = "`zigux/kernel/runtime_loader_contract.zig`"
ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER = "`samples/zigux/runtime_*_loader.zig` scaffolds"
ABSENT_WORKFLOW_MARKER = "`.github/workflows/zigux-bootstrap.yml`"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"

SEQUENCING_UNREGISTERED_GATE_MARKER = (
    "surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`"
)
SEQUENCING_REENTRY_GATE_MARKER = (
    "surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`"
)
SAMPLES_README_FAIL_CLOSED_MARKER = "unregistered function-thread failures fail-closed"
SAMPLES_README_REENTRY_GATE_DETAIL_MARKER = (
    "Treat `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` as the same packet's balanced registration re-entry companion across the initialized and selftest_complete stages"
)
SAMPLES_README_EXIT_ROLLBACK_GUARD_DETAIL_MARKER = (
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig` keeps failed-exit rollback explicit after reusable selftest replay"
)
SAMPLES_README_INITIALIZED_EXIT_MARKER = (
    "The same direct sample now also keeps initialized-stage clean exit explicit through `test \"trace-events sample preserves initialized summary across direct exit without selftest\"`"
)
SAMPLES_README_POST_EXIT_REJECTION_MARKER = "post-exit invalid-lifecycle rejections"
SAMPLES_README_SUMMARY_STABILITY_MARKER = (
    "initialized-before/after, selftest_complete-before/after, and exited-before/after summary-stability checks"
)
SURVEY_NOTE_WITNESS_MARKER = "Current `master` also now keeps one direct family-local `zigux/tests/runtime_*` witness for that same packet:"
SURVEY_NOTE_SAMPLE_LOCAL_MARKER = "sample-local pilot-module reviewability"
SURVEY_NOTE_INITIALIZED_EXIT_MARKER = (
    'The direct sample also now keeps initialized-stage clean exit explicit: `test "trace-events sample preserves initialized summary across direct exit without selftest"` proves zero selftest runs stay explicit, the initialized summary stays unchanged until `exit()` succeeds, and later lifecycle calls remain rejected without drift.'
)
MODULE_SLICE_ALIGNMENT_MARKER = "The paired family-local survey packet through `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig`"
MODULE_SLICE_BOUNDARY_MARKER = "broader shared runtime-loader packet"
MODULE_SLICE_COLD_STAGE_GUARD_MARKER = (
    'The shipped cold-stage guard in `test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity"` also keeps pre-init `runSelftest()` and `exit()` rejection explicit before the module ever reaches `.initialized`, so the packet distinguishes cold-stage fail-closed behavior from the later initialized-stage clean-exit path.'
)
MODULE_SLICE_INITIALIZED_EXIT_MARKER = (
    'The direct initialized-stage exit proof in `test "trace-events sample preserves initialized summary across direct exit without selftest"` keeps zero selftest runs explicit, preserves the initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.'
)
MANIFEST_ALIGNMENT_FOCUS_MARKER = '"alignment_focus": "sample-local pilot-module reviewability rather than returned shared runtime-loader parity"'
MANIFEST_SURVEY_NOTE_MARKER = '"survey_note_path": "Documentation/zigux/phase9-runtime-trace-events-survey.md"'
MANIFEST_MODULE_SLICE_MARKER = '"module_slice_path": "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"'
MANIFEST_SURVEY_GATE_MARKER = '"surface": "zigux/tests/runtime_trace_events_survey.zig"'
MANIFEST_WORKFLOW_MARKER = '"surface": ".github/workflows/zigux-bootstrap.yml"'
SURVEY_GATE_SURVEY_NOTE_MARKER = '"Documentation/zigux/phase9-runtime-trace-events-survey.md"'
SURVEY_GATE_MODULE_SLICE_MARKER = '"Documentation/zigux/phase9-runtime-trace-events-module-slice.md"'
SURVEY_GATE_MANIFEST_MARKER = '"zigux/tests/runtime_trace_events_manifest.json"'
SURVEY_GATE_WORKFLOW_MARKER = '".github/workflows/zigux-bootstrap.yml"'
WORKFLOW_BOUNDARY_SELF_TEST_MARKER = "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test"
WORKFLOW_BOUNDARY_LIVE_MARKER = "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py"
WORKFLOW_PACKET_SELF_TEST_MARKER = "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test"
WORKFLOW_PACKET_LIVE_MARKER = "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py"
WORKFLOW_TRACE_EVENTS_SAMPLE_MARKER = "zig test samples/zigux/runtime_trace_events.zig"
WORKFLOW_UNREGISTERED_GATE_MARKER = "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig"
WORKFLOW_EXIT_ROLLBACK_GUARD_MARKER = "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
WORKFLOW_REENTRY_GATE_MARKER = "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig"
WORKFLOW_SURVEY_GATE_MARKER = "zig test zigux/tests/runtime_trace_events_survey.zig"

SAMPLE_REQUIRED_MARKERS = [
    '.name = "runtime_trace_events"',
    '.anchor = "samples/trace_events/trace-events-sample.c"',
    ".requires_runtime_substrate = true",
    ".provides_selftest_hook = true",
    "pub fn runSelftest(self: *Self) !EmissionSummary {",
    "pub fn exit(self: *Self) !void {",
    'test "trace-events sample rejects duplicate function-thread registration" {',
    "error.FunctionThreadAlreadyRegistered",
    "const before_duplicate = module.summary();",
    "try std.testing.expectEqual(@as(usize, 1), before_duplicate.registration_depth);",
    "const after_duplicate = module.summary();",
    "try std.testing.expectEqual(before_duplicate.stage, after_duplicate.stage);",
    "try std.testing.expectEqual(before_duplicate.total_events, after_duplicate.total_events);",
    "try std.testing.expectEqualStrings(before_duplicate.last_register_label orelse return error.ExpectedFunctionPayload, after_duplicate.last_register_label orelse return error.ExpectedFunctionPayload);",
    'test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {',
    "try std.testing.expectEqual(ModuleStage.cold, module.stage());",
    "try std.testing.expectEqual(ModuleStage.cold, module.stage());\n    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());",
    "try std.testing.expect(selftest.conditional_paths_checked);",
    "try std.testing.expect(selftest.registration_paths_checked);",
    'test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {',
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_failed_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);",
    "try std.testing.expectError(error.OutstandingRegistration, module.exit());",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, after_failed_exit.stage);",
    "try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);",
    "try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);",
    "try std.testing.expectEqual(before_failed_exit.last_main_emitted_events, after_failed_exit.last_main_emitted_events);",
    "try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, after_failed_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
    "try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);",
    "try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);",
    "try std.testing.expectEqual(before_exit.registration_depth, after_exit.registration_depth);",
    'test "trace-events sample keeps rejected re-selftest rollback explicit" {',
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(13));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(15));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());",
    "try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);",
    "try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);",
    "try std.testing.expectEqual(selftest_complete_summary.total_events, exited_summary.total_events);",
    "try std.testing.expectEqual(selftest_complete_summary.registration_depth, exited_summary.registration_depth);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_summary.stage);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_complete_summary.selftest_runs);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_rejected_selftest.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);",
    "try std.testing.expectEqual(ModuleStage.exited, before_rejected_exit_selftest.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);",
    "error.OutstandingRegistration",
]

UNREGISTERED_GATE_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample keeps unregistered function-thread failures fail-closed" {',
    "fn expectSummaryStable(before: RuntimeTraceEventsSummary, after: RuntimeTraceEventsSummary) !void {",
    "try std.testing.expectEqual(ModuleStage.initialized, initialized_before.stage);",
    "try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(3));",
    "try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(3));\n    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());",
    "try expectSummaryStable(initialized_before, initialized_after);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_before.stage);",
    "try std.testing.expectEqual(@as(usize, 2), selftest_complete_before.main_iterations);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.fn_iterations);",
    "try std.testing.expectEqual(@as(usize, 10), selftest_complete_before.main_thread_events);",
    "try std.testing.expectEqual(@as(usize, 2), selftest_complete_before.fn_thread_events);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 12), selftest_complete_before.total_events);",
    "try std.testing.expectEqual(@as(i32, 5), selftest_complete_before.last_main_count);",
    "try std.testing.expectEqual(@as(i32, 1), selftest_complete_before.last_fn_count);",
    "try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(7));\n    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());",
    "try expectSummaryStable(selftest_complete_before, selftest_complete_after);",
    "try std.testing.expectEqualStrings(selftest_complete_before.last_unregister_label orelse return error.ExpectedUnregisterLabel, selftest_complete_after.last_unregister_label orelse return error.ExpectedUnregisterLabel);",
    "try module.exit();",
    "const exited_before = module.summary();",
    "try std.testing.expectEqual(ModuleStage.exited, exited_before.stage);",
    "try std.testing.expectEqual(@as(usize, 1), exited_before.exit_runs);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(9));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(11));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());",
    "const exited_after = module.summary();",
    "try expectSummaryStable(exited_before, exited_after);",
]

REENTRY_GATE_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages" {',
    "try std.testing.expectEqual(ModuleStage.initialized, initialized_before.stage);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_before.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_before.main_iterations);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_iterations);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_thread_events);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_before.total_events);",
    "try module.registerFunctionThread();",
    "const initialized_registered_before_duplicate = module.summary();",
    "try std.testing.expectEqual(ModuleStage.initialized, initialized_registered_before_duplicate.stage);",
    "try std.testing.expectEqual(@as(usize, 1), initialized_registered_before_duplicate.registration_depth);",
    'try std.testing.expectEqualStrings("foo_bar_reg", initialized_registered_before_duplicate.last_register_label orelse return error.ExpectedRegisterLabel);',
    "try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());",
    "const initialized_registered_after_duplicate = module.summary();",
    "try std.testing.expect(std.meta.eql(initialized_registered_before_duplicate, initialized_registered_after_duplicate));",
    "const initialized_replay = try module.emitFunctionIteration(3);",
    "try std.testing.expectEqual(@as(usize, 2), initialized_replay);",
    "try module.unregisterFunctionThread();",
    "try std.testing.expectEqual(ModuleStage.initialized, initialized_after.stage);",
    "try std.testing.expectEqual(@as(usize, 0), initialized_after.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 1), initialized_after.fn_iterations);",
    "try std.testing.expectEqual(@as(usize, 2), initialized_after.fn_thread_events);",
    "try std.testing.expectEqual(@as(usize, 2), initialized_after.total_events);",
    "try std.testing.expectEqual(@as(?usize, 2), initialized_after.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(i32, 3), initialized_after.last_fn_count);",
    'try std.testing.expectEqualStrings("foo_bar_reg", initialized_after.last_register_label orelse return error.ExpectedRegisterLabel);',
    'try std.testing.expectEqualStrings("foo_bar_unreg", initialized_after.last_unregister_label orelse return error.ExpectedUnregisterLabel);',
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.init());",
    "const initialized_after_reinit = module.summary();",
    "try std.testing.expect(std.meta.eql(initialized_after, initialized_after_reinit));",
    "_ = try module.runSelftest();",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_before.stage);",
    "try std.testing.expectEqual(@as(usize, 0), selftest_before.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_before.main_iterations);",
    "try std.testing.expectEqual(@as(usize, 2), selftest_before.fn_iterations);",
    "try std.testing.expectEqual(@as(usize, 4), selftest_before.fn_thread_events);",
    "try std.testing.expectEqual(@as(usize, 10), selftest_before.total_events);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_before.selftest_runs);",
    "try std.testing.expectEqual(@as(i32, 1), selftest_before.last_fn_count);",
    "const selftest_registered_before_duplicate = module.summary();",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_registered_before_duplicate.stage);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_registered_before_duplicate.registration_depth);",
    "const selftest_registered_after_duplicate = module.summary();",
    "try std.testing.expect(std.meta.eql(selftest_registered_before_duplicate, selftest_registered_after_duplicate));",
    "const selftest_replay = try module.emitFunctionIteration(11);",
    "try std.testing.expectEqual(@as(usize, 2), selftest_replay);",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_after.stage);",
    "try std.testing.expectEqual(@as(usize, 0), selftest_after.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_after.main_iterations);",
    "try std.testing.expectEqual(@as(usize, 3), selftest_after.fn_iterations);",
    "try std.testing.expectEqual(@as(usize, 6), selftest_after.fn_thread_events);",
    "try std.testing.expectEqual(@as(usize, 12), selftest_after.total_events);",
    "try std.testing.expectEqual(@as(usize, 1), selftest_after.selftest_runs);",
    "try std.testing.expectEqual(@as(?usize, 2), selftest_after.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(i32, 11), selftest_after.last_fn_count);",
    'try std.testing.expectEqualStrings("foo_bar_reg", selftest_after.last_register_label orelse return error.ExpectedRegisterLabel);',
    'try std.testing.expectEqualStrings("foo_bar_unreg", selftest_after.last_unregister_label orelse return error.ExpectedUnregisterLabel);',
    "const before_exit = module.summary();",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 1), before_exit.main_iterations);",
    "try std.testing.expectEqual(@as(usize, 3), before_exit.fn_iterations);",
    "try std.testing.expectEqual(@as(usize, 6), before_exit.main_thread_events);",
    "try std.testing.expectEqual(@as(usize, 6), before_exit.fn_thread_events);",    "try std.testing.expectEqual(@as(usize, 12), before_exit.total_events);",
    "try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);",
    "try std.testing.expectEqual(@as(usize, 1), before_exit.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);",
    "try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(@as(i32, 11), before_exit.last_fn_count);",
    'try std.testing.expectEqualStrings("foo_bar_reg", before_exit.last_register_label orelse return error.ExpectedRegisterLabel);',
    'try std.testing.expectEqualStrings("foo_bar_unreg", before_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);',
    "try module.exit();",
    "const after_exit = module.summary();",
    "try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.init_runs);",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
    "try std.testing.expectEqual(before_exit.registration_depth, after_exit.registration_depth);",
    "try std.testing.expectEqual(before_exit.main_iterations, after_exit.main_iterations);",
    "try std.testing.expectEqual(before_exit.fn_iterations, after_exit.fn_iterations);",
    "try std.testing.expectEqual(before_exit.main_thread_events, after_exit.main_thread_events);",
    "try std.testing.expectEqual(before_exit.fn_thread_events, after_exit.fn_thread_events);",
    "try std.testing.expectEqual(before_exit.total_events, after_exit.total_events);",
    "try std.testing.expectEqual(before_exit.last_fn_emitted_events, after_exit.last_fn_emitted_events);",
    "try std.testing.expectEqual(before_exit.last_fn_count, after_exit.last_fn_count);",
    "try std.testing.expectEqualStrings(before_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);",
    "try std.testing.expectEqualStrings(before_exit.last_register_label orelse return error.ExpectedRegisterLabel, after_exit.last_register_label orelse return error.ExpectedRegisterLabel);",
    "try std.testing.expectEqualStrings(before_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel, after_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);",
    "const exited_before_rejected_main = module.summary();",
    "try std.testing.expectEqual(ModuleStage.exited, exited_before_rejected_main.stage);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(13));",
    "const exited_after_rejected_main = module.summary();",
    "try std.testing.expect(std.meta.eql(exited_before_rejected_main, exited_after_rejected_main));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(15));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());",
    'test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest" {',
    "try std.testing.expectEqual(ModuleStage.initialized, before_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);",
    "try std.testing.expect(std.meta.eql(after_exit, after_rejected_lifecycle));",
]

EXIT_ROLLBACK_GUARD_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {',
    "fn expectSummaryStable(before: RuntimeTraceEventsSummary, after: RuntimeTraceEventsSummary) !void {",
    "_ = try module.runSelftest();",
    "const replayed_main = try module.emitMainIteration(5);",
    "try std.testing.expectEqual(@as(usize, 4), replayed_main);",
    "try module.registerFunctionThread();",
    "const replayed_fn = try module.emitFunctionIteration(15);",
    "try std.testing.expectEqual(@as(usize, 2), replayed_fn);",
    "const before_failed_exit = module.summary();",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_failed_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 2), before_failed_exit.main_iterations);",
    "try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_iterations);",
    "try std.testing.expectEqual(@as(usize, 14), before_failed_exit.total_events);",
    "try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);",
    "try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);",
    "try std.testing.expectError(error.OutstandingRegistration, module.exit());",
    "const after_failed_exit = module.summary();",
    "try expectSummaryStable(before_failed_exit, after_failed_exit);",
    "const replayed_main_after_failed_exit = try module.emitMainIteration(9);",
    "try std.testing.expectEqual(@as(usize, 4), replayed_main_after_failed_exit);",
    "const after_failed_exit_main_replay = module.summary();",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, after_failed_exit_main_replay.stage);",
    "try std.testing.expectEqual(@as(usize, 18), after_failed_exit_main_replay.total_events);",
    "const replayed_fn_after_failed_exit = try module.emitFunctionIteration(17);",
    "try std.testing.expectEqual(@as(usize, 2), replayed_fn_after_failed_exit);",
    "const before_unregister = module.summary();",
    "try std.testing.expectEqual(@as(usize, 20), before_unregister.total_events);",
    "try std.testing.expectEqual(@as(usize, 2), before_unregister.register_transitions);",
    "try module.unregisterFunctionThread();",
    "const before_exit = module.summary();",
    "try std.testing.expectEqual(ModuleStage.selftest_complete, before_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);",
    "try std.testing.expectEqual(@as(usize, 2), before_exit.unregister_transitions);",
    "try module.exit();",
    "const after_exit = module.summary();",
    "try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.init());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(17));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(19));",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());",
    "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
]

FILE_MARKERS = {
    SEQUENCING_PATH: [
        TRACE_EVENTS_SAMPLE_MARKER,
        SELFTEST_HOOK_MARKER,
        LIFECYCLE_MARKER,
        SEQUENCING_UNREGISTERED_GATE_MARKER,
        SEQUENCING_REENTRY_GATE_MARKER,
        ABSENT_SHARED_LOADER_MARKER,
        ABSENT_PHASE9_BUILD_MARKER,
        ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
        ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
        ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER,
    ],
    SURVEY_NOTE_PATH: [
        TRACE_EVENTS_SAMPLE_MARKER,
        UNREGISTERED_GATE_SAMPLE_MARKER,
        EXIT_ROLLBACK_GUARD_SAMPLE_MARKER,
        REENTRY_GATE_SAMPLE_MARKER,
        "`zigux/tests/runtime_trace_events_manifest.json`",
        "`zigux/tests/runtime_trace_events_survey.zig`",
        "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`",
        SELFTEST_HOOK_MARKER,
        LIFECYCLE_MARKER,
        SURVEY_NOTE_WITNESS_MARKER,
        SURVEY_NOTE_SAMPLE_LOCAL_MARKER,
        SURVEY_NOTE_INITIALIZED_EXIT_MARKER,
        ABSENT_PHASE9_BUILD_MARKER,
        ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
        ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
        ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER,
    ],
    MODULE_SLICE_PATH: [
        TRACE_EVENTS_SAMPLE_MARKER,
        UNREGISTERED_GATE_SAMPLE_MARKER,
        EXIT_ROLLBACK_GUARD_SAMPLE_MARKER,
        REENTRY_GATE_SAMPLE_MARKER,
        "`Documentation/zigux/phase9-runtime-trace-events-survey.md`",
        "`zigux/tests/runtime_trace_events_manifest.json`",
        "`zigux/tests/runtime_trace_events_survey.zig`",
        SELFTEST_HOOK_MARKER,
        LIFECYCLE_MARKER,
        MODULE_SLICE_ALIGNMENT_MARKER,
        MODULE_SLICE_BOUNDARY_MARKER,
        MODULE_SLICE_COLD_STAGE_GUARD_MARKER,
        MODULE_SLICE_INITIALIZED_EXIT_MARKER,
        ABSENT_PHASE9_BUILD_MARKER,
    ],
    SAMPLES_README_PATH: [
        TRACE_EVENTS_SAMPLE_MARKER,
        UNREGISTERED_GATE_SAMPLE_MARKER,
        EXIT_ROLLBACK_GUARD_SAMPLE_MARKER,
        SAMPLES_README_FAIL_CLOSED_MARKER,
        REENTRY_GATE_SAMPLE_MARKER,
        TRACE_EVENTS_PACKET_CHECKER_MARKER,
        SELFTEST_HOOK_MARKER,
        LIFECYCLE_MARKER,
        REENTRY_COMPANION_MARKER,
        EXIT_ROLLBACK_COMPANION_MARKER,
        SAMPLES_README_REENTRY_GATE_DETAIL_MARKER,
        SAMPLES_README_EXIT_ROLLBACK_GUARD_DETAIL_MARKER,
        SAMPLES_README_INITIALIZED_EXIT_MARKER,
        SAMPLES_README_POST_EXIT_REJECTION_MARKER,
        SAMPLES_README_SUMMARY_STABILITY_MARKER,
        ABSENT_SHARED_LOADER_MARKER,
        ABSENT_PHASE9_BUILD_MARKER,
        ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
        ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
        ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER,
        ABSENT_WORKFLOW_MARKER,
        PHASE2_CONF_BRIDGE_MARKER,
        PHASE2_CONFDATA_BRIDGE_MARKER,
        PHASE3_EXPORTS_MARKER,
        PHASE3_EXPORT_SHIM_MARKER,
    ],
    MANIFEST_PATH: [
        '"lane_key": "P9-L09"',
        '"phase": "Phase 9"',
        '"survey_summary": {',
        MANIFEST_ALIGNMENT_FOCUS_MARKER,
        MANIFEST_SURVEY_NOTE_MARKER,
        MANIFEST_MODULE_SLICE_MARKER,
        MANIFEST_SURVEY_GATE_MARKER,
        MANIFEST_WORKFLOW_MARKER,
    ],
    SURVEY_GATE_PATH: [
        SURVEY_GATE_SURVEY_NOTE_MARKER,
        SURVEY_GATE_MODULE_SLICE_MARKER,
        SURVEY_GATE_MANIFEST_MARKER,
        SURVEY_GATE_WORKFLOW_MARKER,
        "phase9 trace-events survey packet matches the narrow current-master pilot-module story",
        ".provides_selftest_hook = true",
        "initialized, selftest_complete, and exited lifecycle tracking",
    ],
    SAMPLE_PATH: SAMPLE_REQUIRED_MARKERS,
    UNREGISTERED_GATE_SAMPLE_PATH: UNREGISTERED_GATE_REQUIRED_MARKERS,
    REENTRY_GATE_SAMPLE_PATH: REENTRY_GATE_REQUIRED_MARKERS,
    EXIT_ROLLBACK_GUARD_SAMPLE_PATH: EXIT_ROLLBACK_GUARD_REQUIRED_MARKERS,
    WORKFLOW_PATH: [
        WORKFLOW_BOUNDARY_SELF_TEST_MARKER,
        WORKFLOW_BOUNDARY_LIVE_MARKER,
        WORKFLOW_PACKET_SELF_TEST_MARKER,
        WORKFLOW_PACKET_LIVE_MARKER,
        WORKFLOW_TRACE_EVENTS_SAMPLE_MARKER,
        WORKFLOW_UNREGISTERED_GATE_MARKER,
        WORKFLOW_EXIT_ROLLBACK_GUARD_MARKER,
        WORKFLOW_REENTRY_GATE_MARKER,
        WORKFLOW_SURVEY_GATE_MARKER,
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text(rel_path: str, markers: list[str]) -> str:
    if rel_path.endswith(".md"):
        return "\n".join(["# fixture", "", *markers, ""])
    return "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in FILE_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in FILE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        write_text(base / rel_path, build_fixture_text(rel_path, markers))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-runtime-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                if marker not in current:
                    raise SystemExit(f"fixture missing expected marker before mutation: {rel_path}:{marker}")
                write_text(base / rel_path, current.replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
        print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SEQUENCING_MARKER_COUNT={len(FILE_MARKERS[SEQUENCING_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SURVEY_NOTE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_NOTE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_MODULE_SLICE_MARKER_COUNT={len(FILE_MARKERS[MODULE_SLICE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLES_README_MARKER_COUNT={len(FILE_MARKERS[SAMPLES_README_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_MANIFEST_MARKER_COUNT={len(FILE_MARKERS[MANIFEST_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SURVEY_GATE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_GATE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLE_MARKER_COUNT={len(FILE_MARKERS[SAMPLE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_UNREGISTERED_GATE_MARKER_COUNT={len(FILE_MARKERS[UNREGISTERED_GATE_SAMPLE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_REENTRY_GATE_MARKER_COUNT={len(FILE_MARKERS[REENTRY_GATE_SAMPLE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_EXIT_ROLLBACK_GUARD_MARKER_COUNT={len(FILE_MARKERS[EXIT_ROLLBACK_GUARD_SAMPLE_PATH])}")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_WORKFLOW_MARKER_COUNT={len(FILE_MARKERS[WORKFLOW_PATH])}")
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
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SEQUENCING_MARKER_COUNT={len(FILE_MARKERS[SEQUENCING_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SURVEY_NOTE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_NOTE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_MODULE_SLICE_MARKER_COUNT={len(FILE_MARKERS[MODULE_SLICE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLES_README_MARKER_COUNT={len(FILE_MARKERS[SAMPLES_README_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_MANIFEST_MARKER_COUNT={len(FILE_MARKERS[MANIFEST_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SURVEY_GATE_MARKER_COUNT={len(FILE_MARKERS[SURVEY_GATE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLE_MARKER_COUNT={len(FILE_MARKERS[SAMPLE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_UNREGISTERED_GATE_MARKER_COUNT={len(FILE_MARKERS[UNREGISTERED_GATE_SAMPLE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_REENTRY_GATE_MARKER_COUNT={len(FILE_MARKERS[REENTRY_GATE_SAMPLE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_EXIT_ROLLBACK_GUARD_MARKER_COUNT={len(FILE_MARKERS[EXIT_ROLLBACK_GUARD_SAMPLE_PATH])}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_WORKFLOW_MARKER_COUNT={len(FILE_MARKERS[WORKFLOW_PATH])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
