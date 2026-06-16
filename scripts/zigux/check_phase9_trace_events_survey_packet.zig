const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_TRACE_EVENTS_SURVEY_PACKET_SELF_TEST=pass";

const MANIFEST_ALIGNMENT_FOCUS_MARKER = [_][]const u8{
    "\"alignment_focus\": \"sample-local pilot-module reviewability rather than returned shared runtime-loader parity\"",
};

const MANIFEST_NEXT_GATE_MARKER = [_][]const u8{
    "\"next_gate\": \"keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family while shared loader work stays parked\"",
};

const SURVEY_GATE_TEST_NAME_MARKER = [_][]const u8{
    "test \"phase9 trace-events survey packet matches the narrow current-master pilot-module story\" {",
};

const SURVEY_GATE_ALIGNMENT_BOUNDARY_MARKER = [_][]const u8{
    "Fail-closes on drift between the survey note, module-slice note, manifest, sequencing note, and surviving sample family.",
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

const SURVEYED_COMMIT_MARKER = [_][]const u8{
    "PHASE9_SURVEYED_COMMIT=70542337d15e9f26941f6a247da00077dddcebe8",
};

const TRACE_EVENTS_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events.zig`",
};

const UNREGISTERED_GATE_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
};

const EXIT_ROLLBACK_GUARD_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
};

const REENTRY_GATE_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
};

const MANIFEST_REFERENCE_MARKER = [_][]const u8{
    "`zigux/tests/runtime_trace_events_manifest.json`",
};

const SURVEY_GATE_REFERENCE_MARKER = [_][]const u8{
    "`zigux/tests/runtime_trace_events_survey.zig`",
};

const MODULE_SLICE_REFERENCE_MARKER = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`",
};

const SELFTEST_HOOK_MARKER = [_][]const u8{
    "`.provides_selftest_hook = true`",
};

const LIFECYCLE_MARKER = [_][]const u8{
    "initialized, selftest_complete, and exited lifecycle tracking",
};

const FAMILY_LOCAL_WITNESS_MARKER = [_][]const u8{
    "direct family-local `zigux/tests/runtime_*` witness",
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

const NO_VALIDATE_PHASE9_MARKER = [_][]const u8{
    "Do not invent `validate-phase9.py`",
};

const MANIFEST_SURVEYED_COMMIT_MARKER = [_][]const u8{
    "\"surveyed_commit\": \"70542337d15e9f26941f6a247da00077dddcebe8\"",
};

const MANIFEST_DIRECT_TEST_FILES_MARKER = [_][]const u8{
    "\"direct_runtime_trace_events_test_files\": 2",
};

const MANIFEST_SAMPLE_FAMILY_COUNT_MARKER = [_][]const u8{
    "\"surviving_sample_family_files\": 4",
};

const MANIFEST_SURVEY_NOTE_PRESENT_MARKER = [_][]const u8{
    "\"survey_note_present\": true",
};

const MANIFEST_MODULE_SLICE_PRESENT_MARKER = [_][]const u8{
    "\"module_slice_present\": true",
};

const MANIFEST_MODULE_SLICE_PATH_MARKER = [_][]const u8{
    "\"module_slice_path\": \"Documentation/zigux/phase9-runtime-trace-events-module-slice.md\"",
};

const MANIFEST_SURVEY_NOTE_PATH_MARKER = [_][]const u8{
    "\"survey_note_path\": \"Documentation/zigux/phase9-runtime-trace-events-survey.md\"",
};

const MANIFEST_PATH_MARKER = [_][]const u8{
    "\"manifest_path\": \"zigux/tests/runtime_trace_events_manifest.json\"",
};

const MANIFEST_LANDED_PILOT_STATE_MARKER = [_][]const u8{
    "\"landed_pilot_state\": \"narrow trace-events sample packet plus family-local survey witness\"",
};

const MANIFEST_SURVEY_GATE_OWNER_MARKER = [_][]const u8{
    "\"surface\": \"zigux/tests/runtime_trace_events_survey.zig\"",
};

const MANIFEST_SURVEY_GATE_ROLE_MARKER = [_][]const u8{
    "\"role\": \"survey_gate\"",
};

const MODULE_SLICE_SURVEY_NOTE_MARKER = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-trace-events-survey.md`",
};

const MODULE_SLICE_MANIFEST_MARKER = [_][]const u8{
    "`zigux/tests/runtime_trace_events_manifest.json`",
};

const MODULE_SLICE_SURVEY_GATE_MARKER = [_][]const u8{
    "`zigux/tests/runtime_trace_events_survey.zig`",
};

const MODULE_SLICE_ALIGNMENT_MARKER = [_][]const u8{
    "sample-local pilot-module reviewability",
};

const MODULE_SLICE_ABSENT_SHARED_LOADER_MARKER = [_][]const u8{
    "broader shared runtime-loader packet",
};

const SURVEY_GATE_SURVEYED_COMMIT_HELPER_MARKER = [_][]const u8{
    "fn expectSurveyedCommitMarker(note: []const u8, surveyed_commit: []const u8) !void {",
};

const SURVEY_GATE_SURVEY_NOTE_PATH_MARKER = [_][]const u8{
    "\"Documentation/zigux/phase9-runtime-trace-events-survey.md\"",
};

const SURVEY_GATE_MODULE_SLICE_PATH_MARKER = [_][]const u8{
    "\"Documentation/zigux/phase9-runtime-trace-events-module-slice.md\"",
};

const SURVEY_GATE_MANIFEST_PATH_MARKER = [_][]const u8{
    "\"zigux/tests/runtime_trace_events_manifest.json\"",
};

const SURVEY_GATE_SURVEY_GATE_PATH_MARKER = [_][]const u8{
    "\"zigux/tests/runtime_trace_events_survey.zig\"",
};

const SURVEY_GATE_LANE_KEY_MARKER = [_][]const u8{
    "try std.testing.expectEqualStrings(\"P9-L09\", manifest.lane_key);",
};

const SURVEY_GATE_LANDED_PILOT_STATE_MARKER = [_][]const u8{
    "\"narrow trace-events sample packet plus family-local survey witness\"",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MANIFEST_ALIGNMENT_FOCUS_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_NEXT_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_TEST_NAME_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_ALIGNMENT_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEYED_COMMIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (TRACE_EVENTS_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (EXIT_ROLLBACK_GUARD_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (REENTRY_GATE_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_REFERENCE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_REFERENCE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_REFERENCE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SELFTEST_HOOK_MARKER) |marker| try guard.requireMarker(text, marker);
    for (LIFECYCLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (FAMILY_LOCAL_WITNESS_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_SHARED_LOADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_PHASE9_BUILD_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_LOADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_RUNTIME_LOADER_CONTRACT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (NO_VALIDATE_PHASE9_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_SURVEYED_COMMIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_DIRECT_TEST_FILES_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_SAMPLE_FAMILY_COUNT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_SURVEY_NOTE_PRESENT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MODULE_SLICE_PRESENT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MODULE_SLICE_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_SURVEY_NOTE_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_LANDED_PILOT_STATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_SURVEY_GATE_OWNER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_SURVEY_GATE_ROLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_SURVEY_NOTE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_MANIFEST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_SURVEY_GATE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_ALIGNMENT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_ABSENT_SHARED_LOADER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_SURVEYED_COMMIT_HELPER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_SURVEY_NOTE_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MODULE_SLICE_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MANIFEST_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_SURVEY_GATE_PATH_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_LANE_KEY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_LANDED_PILOT_STATE_MARKER) |marker| try guard.requireMarker(text, marker);
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
