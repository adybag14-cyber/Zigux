const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_SHARED_PACKET_MANIFEST_SELF_TEST=pass";

const SHARED_REVIEW_SURFACES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "scripts/zigux/README.md",
    "samples/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig",
    "scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
};

const DIRECT_RUNTIME_PACKET = [_][]const u8{
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
};

const ADJACENT_FAMILY_LOCAL_SURFACES = [_][]const u8{
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
};

const ABSENT_BACKLOG_FILES = [_][]const u8{
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/kernel/runtime_loader_contract.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
};

const NON_OWNER_BOUNDARIES = [_][]const u8{
    "phase2_config_surface",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "phase3_export_boundary",
    "rust/exports.c",
    "zigux/kernel/export_shim.zig",
    "freeze_map_anchors",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const OWNERSHIP_MAP = [_][]const u8{
    "Documentation/zigux/README.md",
    "P9-L11",
    "Documentation/zigux/review-checklist.md",
    "P9-L11",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "P9-L11",
    "scripts/zigux/README.md",
    "P9-L11",
    "samples/zigux/README.md",
    "P9-L11",
    "zigux/tests/README.md",
    "P9-L11",
    "scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig",
    "P9-L11",
    "scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
    "P9-L11",
    ".github/workflows/zigux-bootstrap.yml",
    "P9-L11",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "P9-L09",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "P9-L09",
    "zigux/tests/runtime_trace_events_manifest.json",
    "P9-L09",
    "zigux/tests/runtime_trace_events_survey.zig",
    "P9-L09",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SHARED_REVIEW_SURFACES) |marker| try guard.requireMarker(text, marker);
    for (DIRECT_RUNTIME_PACKET) |marker| try guard.requireMarker(text, marker);
    for (ADJACENT_FAMILY_LOCAL_SURFACES) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_BACKLOG_FILES) |marker| try guard.requireMarker(text, marker);
    for (NON_OWNER_BOUNDARIES) |marker| try guard.requireMarker(text, marker);
    for (OWNERSHIP_MAP) |marker| try guard.requireMarker(text, marker);
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
