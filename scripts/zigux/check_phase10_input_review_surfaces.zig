const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_INPUT_REVIEW_SURFACES_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
};

const MARKERS = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check_phase10_input_packet.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "Documentation/zigux/phase10-closure-evidence.md",
    "scripts/zigux/check_phase10_input_packet.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "Keep the input-lane helper names `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, and `drivers/virtio/virtio_input_teardown_observation.zig` explicit",
    "scripts/zigux/README.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (MARKERS) |marker| try guard.requireMarker(text, marker);
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
