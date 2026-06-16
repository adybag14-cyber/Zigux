const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_INPUT_SHARED_REMINDER_EVIDENCE_SELF_TEST=pass";

const INPUT_SHARD_MARKERS = [_][]const u8{
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Documentation/zigux/phase10-closure-evidence.md",
    "# Phase 10 Closure Evidence",
    "input lane's helper-local packet stays reviewable",
    "phase10-virtio-input-registration-lifecycle",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "# Phase 10 Virtio Input Survey",
    "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport",
    "Current `master` keeps this input lane reviewable through the bounded helper packet:",
    "phase10-virtio-input-registration-lifecycle",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "# Phase 10, 11, and 13 Tests-Root Review Companion",
    "directly re-readable input packet anchors",
    "returned shared closure packet anchors",
    "scripts/zigux/check_phase10_input_packet.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (INPUT_SHARD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
