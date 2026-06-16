const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_RING_MANIFEST_DESTINATIONS_SELF_TEST=pass";

const EXPECTED_SUMMARY_FIELDS = [_][]const u8{
    "preexisting_ring_callback_enable_present",
    "preexisting_ring_reset_readiness_present",
};

const EXPECTED_DESTINATIONS = [_][]const u8{
    "phase10-callback-enable-helper",
    "drivers/virtio/virtio_ring_callback_enable.zig",
    "phase10-queue-reset-readiness-helper",
    "drivers/virtio/virtio_ring_reset_readiness.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_virtio_ring_manifest.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_SUMMARY_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_DESTINATIONS) |marker| try guard.requireMarker(text, marker);
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
