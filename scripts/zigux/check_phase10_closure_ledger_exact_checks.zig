const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_CLOSURE_LEDGER_EXACT_CHECKS_SELF_TEST=pass";

const REQUIRED_PATHS = [_][]const u8{
    "LEDGER_PATH",
    "MANIFEST_PATH",
    "CLOSURE_DOC_PATH",
};

const CLOSURE_DOC_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase10_bootstrap_route.zig",
    "scripts/zigux/check_phase10_core_packet.zig",
    "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "scripts/zigux/check_phase10_ring_packet.zig",
    "scripts/zigux/check_phase10_input_packet.zig",
    "scripts/zigux/check_phase10_mmio_packet.zig",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "scripts\zigux/validate_phase10.zig",
    "scripts\zigux/validate_phase10_closure.zig",
    "zigux/tests/phase10_build.zig",
    "zigux/Makefile",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_PATHS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_DOC_MARKERS) |marker| try guard.requireMarker(text, marker);
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
