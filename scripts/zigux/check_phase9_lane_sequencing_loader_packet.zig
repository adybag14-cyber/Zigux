const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_LANE_SEQUENCING_LOADER_PACKET_SELF_TEST=pass";

const NOTE_REQUIRED_MARKERS = [_][]const u8{
    "Trusted mixed rereads on 2026-05-21 confirm three distinct current-master Phase 9 postures.",
    "The shared runtime-loader allocator/init-flow and command/environment boundary packet now survives as a narrower direct-readback shared-owner surface",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "keep the Phase 8 command and environment ownership boundary explicit",
    "deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`",
    "`LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
    "the current reminder surfaces now keep the bounded runtime bitmap packet visible",
    "treat any future docs-root or tests-root drift as shared reminder debt to repair one surface at a time",
    "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references",
    "`rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence",
};

const BUILD_REQUIRED_MARKERS = [_][]const u8{
    "b.path(\"runtime_loader_allocator_init_flow.zig\")",
    "b.path(\"../kernel/runtime_loader_command_env_boundary_guard.zig\")",
    "\"phase9-runtime-loader-allocator-init-flow-tests\"",
    "\"phase9-runtime-loader-command-env-boundary-guard-tests\"",
    "\"phase9-runtime-loader-shared-tests\"",
};

const ALLOCATOR_FLOW_REQUIRED_MARKERS = [_][]const u8{
    "const AllocatorHandoff = contract.AllocatorHandoff;",
    "fn makeInitializedPlan(",
    "runtime_loader.prepareRequest(bitmap_plan)",
    "released_without_substrate",
};

const COMMAND_ENV_GUARD_REQUIRED_MARKERS = [_][]const u8{
    "test \"shared runtime loader surface rejects argv and environment control bleed-through\" {",
    "\"command_env\"",
    "\"PERF_EXEC_PATH\"",
    "\"\\\"LINES\\\"\"",
    "\"\\\"COLUMNS\\\"\"",
};

const NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase9_build.zig",
};

const ALLOCATOR_FLOW_PATH = [_][]const u8{
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
};

const COMMAND_ENV_GUARD_PATH = [_][]const u8{
    "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ALLOCATOR_FLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COMMAND_ENV_GUARD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (ALLOCATOR_FLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (COMMAND_ENV_GUARD_PATH) |marker| try guard.requireMarker(text, marker);
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
