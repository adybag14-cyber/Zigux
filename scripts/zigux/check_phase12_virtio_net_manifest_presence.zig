const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_SELF_TEST=pass";

const REQUIRED_PRESENCE_FLAGS = [_][]const u8{
    "preexisting_phase10_build_present",
    "zigux/tests/phase10_build.zig",
    "preexisting_virtio_core_zig_present",
    "drivers/virtio/virtio.zig",
    "preexisting_virtio_ring_zig_present",
    "drivers/virtio/virtio_ring.zig",
    "preexisting_virtio_input_zig_present",
    "drivers/virtio/virtio_input.zig",
    "preexisting_phase12_build_present",
    "zigux/tests/phase12_build.zig",
    "preexisting_phase12_virtio_net_survey_present",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "preexisting_phase12_survey_note_present",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "preexisting_virtio_net_queue_resume_zig_present",
    "drivers/net/virtio_net_queue_resume.zig",
    "preexisting_virtio_net_receive_refill_replay_zig_present",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "preexisting_virtio_net_transmit_recycle_zig_present",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "preexisting_virtio_net_post_reset_replay_zig_present",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "preexisting_virtio_net_throughput_parity_zig_present",
    "drivers/net/virtio_net_throughput_parity.zig",
    "preexisting_phase12_virtio_net_queue_resume_present",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "preexisting_phase12_virtio_net_receive_refill_replay_present",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "preexisting_phase12_virtio_net_transmit_recycle_present",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "preexisting_phase12_virtio_net_post_reset_replay_present",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "preexisting_phase12_virtio_net_throughput_parity_present",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "preexisting_virtio_net_zig_present",
    "drivers/net/virtio_net.zig",
    "preexisting_phase12_virtio_net_zig_present",
    "zigux/tests/phase12_virtio_net.zig",
    "preexisting_phase12_virtio_net_syntax_lab_present",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "preexisting_phase12_virtio_net_syntax_lab_build_present",
    "zigux/tests/phase12_virtio_net_syntax_lab_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_PRESENCE_FLAGS) |marker| try guard.requireMarker(text, marker);
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
