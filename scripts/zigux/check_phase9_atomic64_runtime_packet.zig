const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_ATOMIC64_RUNTIME_PACKET_SELF_TEST=pass";

const CATALOG_PATH = [_][]const u8{
    "scripts/zigux/phase9_catalog.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/runtime_pilot_manifest.json",
};

const PHASE9_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase9_build.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const SAMPLE_PATH = [_][]const u8{
    "samples/zigux/runtime_atomic64.zig",
};

const LOADER_PATH = [_][]const u8{
    "samples/zigux/runtime_atomic64_loader.zig",
};

const MODULE_PATH = [_][]const u8{
    "zigux/tests/runtime_atomic64_module.zig",
};

const DIFF_PATH = [_][]const u8{
    "zigux/tests/runtime_atomic64_diff.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (CATALOG_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE9_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (LOADER_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_PATH) |marker| try guard.requireMarker(text, marker);
    for (DIFF_PATH) |marker| try guard.requireMarker(text, marker);
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
