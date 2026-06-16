const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY_SELF_TEST=pass";

const REQUIRED_REFERENCE_SAMPLE_EVIDENCE = [_][]const u8{
    "samples/zigux",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/review-checklist.md",
};

const REQUIRED_RUNTIME_STARTER_EVIDENCE = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig",
    "scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
    "samples/zigux/README.md",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_direct_init_contract.zig",
    "samples/zigux/runtime_bitmap_cold_stage_guard.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/kernel/runtime_loader_contract.zig",
    "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/runtime_trace_events_loader_substrate_drift.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_closure_manifest.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_REFERENCE_SAMPLE_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_RUNTIME_STARTER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
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
