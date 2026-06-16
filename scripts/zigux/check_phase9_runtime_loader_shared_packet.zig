const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_RUNTIME_LOADER_SHARED_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "DOCS_README",
    "REVIEW_CHECKLIST",
    "LANE_NOTE",
    "OWNERSHIP_MAP",
    "README",
    "CATALOG",
    "CATALOG_SELFTEST",
    "ATOMIC64_PACKET",
    "REVIEW_BOUNDARIES",
    "FREEZE_BOUNDARIES",
    "BUILD_ONLY_SURFACE",
    "TRACE_EVENTS_PACKET",
    "TRACE_EVENTS_DIRECT",
    "TRACE_EVENTS_SUMMARY",
    "VALIDATOR",
    "MANIFEST",
    "PHASE9_BUILD",
    "RUNTIME_LOADER",
    "RUNTIME_LOADER_CONTRACT",
    "RUNTIME_LOADER_BOUNDARY_GUARD",
    "RUNTIME_LOADER_ALLOCATOR_INIT_FLOW",
    "RUNTIME_BITMAP_LOADER",
    "RUNTIME_KRETPROBE_LOADER",
};

const CHECKERS = [_][]const u8{
    "CATALOG_SELFTEST",
    "ATOMIC64_PACKET",
    "REVIEW_BOUNDARIES",
    "FREEZE_BOUNDARIES",
    "BUILD_ONLY_SURFACE",
    "TRACE_EVENTS_PACKET",
    "TRACE_EVENTS_DIRECT",
    "TRACE_EVENTS_SUMMARY",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (CHECKERS) |marker| try guard.requireMarker(text, marker);
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
