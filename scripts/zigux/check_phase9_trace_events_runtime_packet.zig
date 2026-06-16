const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_TRACE_EVENTS_DIRECT_SUMMARY_SELF_TEST=pass";

const SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const SURVEY_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
};

const MODULE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
};

const MODULE_WITNESS_PATH = [_][]const u8{
    "zigux/tests/runtime_trace_events_module.zig",
};

const SAMPLES_README_PATH = [_][]const u8{
    "samples/zigux/README.md",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/runtime_trace_events_manifest.json",
};

const SURVEY_GATE_PATH = [_][]const u8{
    "zigux/tests/runtime_trace_events_survey.zig",
};

const PHASE9_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase9_build.zig",
};

const LOADER_SUBSTRATE_DRIFT_PATH = [_][]const u8{
    "zigux/tests/runtime_trace_events_loader_substrate_drift.zig",
};

const SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events.zig",
};

const UNREGISTERED_GATE_SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
};

const REENTRY_GATE_SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
};

const EXIT_ROLLBACK_GUARD_SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
};

const REINIT_ROLLBACK_GUARD_SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
};

const REINIT_REEXIT_GUARD_SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
};

const DIRECT_SUMMARY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase9_trace_events_direct_summary.zig",
};

const SUMMARY_PRESERVATION_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase9_trace_events_summary_preservation.zig",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const PHASE2_CONF_BRIDGE_MARKER = [_][]const u8{
    "`scripts/zigux/kconfig/conf_bridge.zig`",
};

const PHASE2_CONFDATA_BRIDGE_MARKER = [_][]const u8{
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
};

const PHASE3_EXPORTS_MARKER = [_][]const u8{
    "`rust/exports.c`",
};

const PHASE3_EXPORT_SHIM_MARKER = [_][]const u8{
    "`zigux/kernel/export_shim.zig`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_WITNESS_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE9_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (LOADER_SUBSTRATE_DRIFT_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (UNREGISTERED_GATE_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (REENTRY_GATE_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (EXIT_ROLLBACK_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (REINIT_ROLLBACK_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (REINIT_REEXIT_GUARD_SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (DIRECT_SUMMARY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (SUMMARY_PRESERVATION_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_CONF_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_CONFDATA_BRIDGE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_EXPORTS_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_EXPORT_SHIM_MARKER) |marker| try guard.requireMarker(text, marker);
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
