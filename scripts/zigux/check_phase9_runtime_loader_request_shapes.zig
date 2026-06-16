const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "test \"shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned\" {",
    "        \"runtime_bitmap\",",
    "        \"lib/test_bitmap.c\",",
    "        \"runtime_kretprobe\",",
    "        \"samples/kprobes/kretprobe_example.c\",",
    "    try expectInitializedSharedRequestShape(bitmap_plan, .arena);",
    "    try expectInitializedSharedRequestShape(kretprobe_plan, .caller_provided);",
    "    var bitmap_request = try runtime_loader.prepareRequest(bitmap_plan);",
    "    var kretprobe_request = try runtime_loader.prepareRequest(kretprobe_plan);",
    "    const bitmap_pending = try bitmap_request.requestRuntimeLoad();",
    "    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();",
    "    try bitmap_request.releaseWithoutSubstrate();",
    "    try kretprobe_request.releaseWithoutSubstrate();",
};

const EXACT_ONCE_MARKERS = [_][]const u8{
    "test \"shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned\" {",
    "    try expectInitializedSharedRequestShape(bitmap_plan, .arena);",
    "    try expectInitializedSharedRequestShape(kretprobe_plan, .caller_provided);",
};

const REQUEST_SHAPES_PATH = [_][]const u8{
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUEST_SHAPES_PATH) |marker| try guard.requireMarker(text, marker);
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
