const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_LEDGER_SCOREBOARD_AUTHORITY_SELF_TEST=pass";

const REQUIRED_SCOREBOARD_ROWS = [_][]const u8{
    "virtqueue_wrappersPHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCEdrivers/virtio/virtio_ring_registration_summary.zigdrivers/virtio/virtio_ring_used_buffer_poll.zig",
    "lab_only_driver_validationPHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCEzigux/tests/phase10_virtio_ring_queue_build.zigdrivers/virtio/virtio_input_registration_preflight.zigzigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_closure_manifest.json",
};

const LEDGER_PATH = [_][]const u8{
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
};

const RETAINED_SCOREBOARD_HEADING = [_][]const u8{
    "Manifest-backed scoreboard refreshes retained here for the shared checker route:",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_SCOREBOARD_ROWS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (LEDGER_PATH) |marker| try guard.requireMarker(text, marker);
    for (RETAINED_SCOREBOARD_HEADING) |marker| try guard.requireMarker(text, marker);
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
