const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_SHARED_CHURN_FILTER_SELF_TEST=pass";

const LIVE_INPUT_PACKET_MARKERS = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "\"id\": \"phase10-virtio-input-teardown-preflight-helper\"",
};

const SHARED_FILTER_REQUIRED_MARKERS = [_][]const u8{
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "queue-callback-preflight, registration-preflight, teardown-preflight, status-drain, and teardown-observation replays explicit here",
    "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion now that exact direct-path readback rematerializes it too.",
};

const SHARED_FILTER_FORBIDDEN_MARKERS = [_][]const u8{
    "while exact direct-path readback in this runtime still misses it",
    "queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays explicit here",
};

const COMPANION_REQUIRED_MARKERS = [_][]const u8{
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion now that exact direct-path readback rematerializes it too.",
};

const TESTS_README_REQUIRED_MARKERS = [_][]const u8{
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "queue-callback-preflight, registration-preflight, teardown-preflight, status-drain, and teardown-observation replays explicit here",
};

const SCRIPTS_README_REQUIRED_MARKERS = [_][]const u8{
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (LIVE_INPUT_PACKET_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_FILTER_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_FILTER_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COMPANION_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
