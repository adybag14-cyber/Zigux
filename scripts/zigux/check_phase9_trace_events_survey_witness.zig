const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_TRACE_EVENTS_SURVEY_WITNESS_SELF_TEST=pass";

const INITIALIZED_EXIT_MARKER = [_][]const u8{
    "test \"trace-events sample preserves initialized summary across direct exit without selftest\"",
};

const MANIFEST_ALIGNMENT_MARKER = [_][]const u8{
    "\"alignment_focus\": \"sample-local pilot-module reviewability rather than returned shared runtime-loader parity\"",
};

const MANIFEST_NEXT_GATE_MARKER = [_][]const u8{
    "\"next_gate\": \"keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family while shared loader work stays parked\"",
};

const SURVEY_NOTE_REQUIRED_MARKERS = [_][]const u8{
    "SURVEYED_COMMIT_MARKER",
    "TRACE_EVENTS_SAMPLE_MARKER",
    "UNREGISTERED_GATE_MARKER",
    "EXIT_ROLLBACK_GUARD_MARKER",
    "REENTRY_GATE_MARKER",
    "MANIFEST_FILE_MARKER",
    "SURVEY_GATE_MARKER",
    "MODULE_SLICE_FILE_MARKER",
    "SELFTEST_HOOK_MARKER",
    "LIFECYCLE_MARKER",
    "WITNESS_MARKER",
    "INITIALIZED_EXIT_MARKER",
    "FAIL_CLOSED_MARKER",
    "EXIT_ROLLBACK_MARKER",
    "REENTRY_MARKER",
    "ABSENT_PHASE9_BUILD_MARKER",
    "ABSENT_RUNTIME_LOADER_MARKER",
    "ABSENT_RUNTIME_LOADER_CONTRACT_MARKER",
};

const MODULE_SLICE_REQUIRED_MARKERS = [_][]const u8{
    "SURVEYED_COMMIT_MARKER",
    "TRACE_EVENTS_SAMPLE_MARKER",
    "UNREGISTERED_GATE_MARKER",
    "EXIT_ROLLBACK_GUARD_MARKER",
    "REENTRY_GATE_MARKER",
    "MANIFEST_FILE_MARKER",
    "SURVEY_GATE_MARKER",
    "SELFTEST_HOOK_MARKER",
    "LIFECYCLE_MARKER",
    "SAMPLE_LOCAL_ALIGNMENT_MARKER",
    "INITIALIZED_EXIT_MARKER",
    "ABSENT_SHARED_LOADER_MARKER",
    "ABSENT_PHASE9_BUILD_MARKER",
};

const MANIFEST_REQUIRED_MARKERS = [_][]const u8{
    "MANIFEST_ALIGNMENT_MARKER",
    "MANIFEST_NEXT_GATE_MARKER",
    "\"surface\": \"Documentation/zigux/phase9-runtime-trace-events-survey.md\"",
    "\"surface\": \"zigux/tests/runtime_trace_events_manifest.json\"",
    "\"surface\": \"zigux/tests/runtime_trace_events_survey.zig\"",
    "\"surface\": \"Documentation/zigux/phase9-runtime-trace-events-module-slice.md\"",
    "\"surface\": \"Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md\"",
    "\"surface\": \".github/workflows/zigux-bootstrap.yml\"",
};

const SURVEY_GATE_REQUIRED_MARKERS = [_][]const u8{
    "SURVEY_GATE_ASSERTION_MARKER",
    "try expectContains(survey_note, \"test \\\"trace-events sample preserves initialized summary across direct exit without selftest\\\"\");",
    "try expectContains(module_slice_note, \"sample-local pilot-module reviewability\");",
    "try expectContains(sequencing_note, \"`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`\");",
    "try expectContains(workflow_file, \"zig test zigux/tests/runtime_trace_events_survey.zig\");",
};

const SEQUENCING_REQUIRED_MARKERS = [_][]const u8{
    "TRACE_EVENTS_SAMPLE_MARKER",
    "UNREGISTERED_GATE_MARKER",
    "EXIT_ROLLBACK_GUARD_MARKER",
    "REENTRY_GATE_MARKER",
    "MANIFEST_FILE_MARKER",
    "SURVEY_GATE_MARKER",
    "SELFTEST_HOOK_MARKER",
    "LIFECYCLE_MARKER",
    "ABSENT_SHARED_LOADER_MARKER",
    "WORKFLOW_FILE_MARKER",
};

const WORKFLOW_REQUIRED_MARKERS = [_][]const u8{
    "WORKFLOW_SELF_TEST_MARKER",
    "WORKFLOW_LIVE_MARKER",
    "WORKFLOW_SAMPLE_MARKER",
    "WORKFLOW_UNREGISTERED_MARKER",
    "WORKFLOW_EXIT_GUARD_MARKER",
    "WORKFLOW_REENTRY_MARKER",
    "WORKFLOW_SURVEY_GATE_MARKER",
};

const SAMPLE_REQUIRED_MARKERS = [_][]const u8{
    "SELFTEST_HOOK_MARKER",
    "INITIALIZED_EXIT_MARKER",
};

const UNREGISTERED_REQUIRED_MARKERS = [_][]const u8{
    "phase9 trace-events sample keeps unregistered function-thread failures fail-closed",
};

const EXIT_GUARD_REQUIRED_MARKERS = [_][]const u8{
    "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay",
};

const REENTRY_REQUIRED_MARKERS = [_][]const u8{
    "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages",
};

const SURVEY_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
};

const MODULE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/runtime_trace_events_manifest.json",
};

const SURVEY_GATE_PATH = [_][]const u8{
    "zigux/tests/runtime_trace_events_survey.zig",
};

const SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events.zig",
};

const UNREGISTERED_GATE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
};

const EXIT_ROLLBACK_GUARD_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
};

const REENTRY_GATE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
};

const SURVEYED_COMMIT_MARKER = [_][]const u8{
    "PHASE9_SURVEYED_COMMIT=70542337d15e9f26941f6a247da00077dddcebe8",
};

const TRACE_EVENTS_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events.zig`",
};

const UNREGISTERED_GATE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
};

const EXIT_ROLLBACK_GUARD_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
};

const REENTRY_GATE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
};

const MANIFEST_FILE_MARKER = [_][]const u8{
    "`zigux/tests/runtime_trace_events_manifest.json`",
};

const SURVEY_GATE_MARKER = [_][]const u8{
    "`zigux/tests/runtime_trace_events_survey.zig`",
};

const MODULE_SLICE_FILE_MARKER = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`",
};

const SEQUENCING_NOTE_MARKER = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
};

const WORKFLOW_FILE_MARKER = [_][]const u8{
    "`.github/workflows/zigux-bootstrap.yml`",
};

const SELFTEST_HOOK_MARKER = [_][]const u8{
    "`.provides_selftest_hook = true`",
};

const LIFECYCLE_MARKER = [_][]const u8{
    "initialized, selftest_complete, and exited lifecycle tracking",
};

const WITNESS_MARKER = [_][]const u8{
    "direct family-local `zigux/tests/runtime_*` witness",
};

const SAMPLE_LOCAL_ALIGNMENT_MARKER = [_][]const u8{
    "sample-local pilot-module reviewability rather than returned shared runtime-loader parity",
};

const FAIL_CLOSED_MARKER = [_][]const u8{
    "unregistered function-thread failures fail-closed",
};

const EXIT_ROLLBACK_MARKER = [_][]const u8{
    "failed-exit rollback explicit after reusable selftest replay",
};

const REENTRY_MARKER = [_][]const u8{
    "balanced function-thread registration reusable before and after selftest",
};

const ABSENT_SHARED_LOADER_MARKER = [_][]const u8{
    "does not currently expose the broader shared runtime-loader packet",
};

const ABSENT_PHASE9_BUILD_MARKER = [_][]const u8{
    "`zigux/tests/phase9_build.zig`",
};

const ABSENT_RUNTIME_LOADER_MARKER = [_][]const u8{
    "`zigux/kernel/runtime_loader.zig`",
};

const ABSENT_RUNTIME_LOADER_CONTRACT_MARKER = [_][]const u8{
    "`zigux/kernel/runtime_loader_contract.zig`",
};

const ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER = [_][]const u8{
    "`samples/zigux/runtime_*_loader.zig` scaffolds",
};

const WORKFLOW_SELF_TEST_MARKER = [_][]const u8{
    "Self-test current Phase 9 trace-events runtime packet checker",
};

const WORKFLOW_LIVE_MARKER = [_][]const u8{
    "Check current Phase 9 trace-events runtime packet",
};

const WORKFLOW_SAMPLE_MARKER = [_][]const u8{
    "zig test samples/zigux/runtime_trace_events.zig",
};

const WORKFLOW_UNREGISTERED_MARKER = [_][]const u8{
    "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig",
};

const WORKFLOW_EXIT_GUARD_MARKER = [_][]const u8{
    "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
};

const WORKFLOW_REENTRY_MARKER = [_][]const u8{
    "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
};

const WORKFLOW_SURVEY_GATE_MARKER = [_][]const u8{
    "zig test zigux/tests/runtime_trace_events_survey.zig",
};

const SURVEY_GATE_ASSERTION_MARKER = [_][]const u8{
    "try expectContains(survey_note, \"direct family-local `zigux/tests/runtime_*` witness\");",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (INITIALIZED_EXIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_ALIGNMENT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_NEXT_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXIT_GUARD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REENTRY_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_PATH) |marker| try guard.requireMarker(text, marker);
    for (EXIT_ROLLBACK_GUARD_PATH) |marker| try guard.requireMarker(text, marker);
    for (REENTRY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEYED_COMMIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (TRACE_EVENTS_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (EXIT_ROLLBACK_GUARD_MARKER) |marker| try guard.requireMarker(text, marker);
    for (REENTRY_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_FILE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_FILE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_NOTE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_FILE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SELFTEST_HOOK_MARKER) |marker| try guard.requireMarker(text, marker);
    for (LIFECYCLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WITNESS_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_LOCAL_ALIGNMENT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (FAIL_CLOSED_MARKER) |marker| try guard.requireMarker(text, marker);
    for (EXIT_ROLLBACK_MARKER) |marker| try guard.requireMarker(text, marker);
    for (REENTRY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_SHARED_LOADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_PHASE9_BUILD_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_LOADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_LOADER_CONTRACT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_SELF_TEST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_LIVE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_UNREGISTERED_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_EXIT_GUARD_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_REENTRY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_SURVEY_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_ASSERTION_MARKER) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
