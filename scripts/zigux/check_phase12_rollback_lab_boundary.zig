const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_ROLLBACK_LAB_BOUNDARY_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "READINESS_PATH",
    "CLOSURE_PATH",
    "MATRIX_PATH",
    "PHASE12_BUILD_PATH",
};

const FORBIDDEN_BUILD_MARKERS = [_][]const u8{
    "phase12_virtio_scsi_survey_build.zig",
    "phase12_virtio_scsi_repeated_replan_gate.zig",
    "phase12_virtio_scsi_repeated_rollback_gate.zig",
    "phase12_virtio_scsi_packet.zig",
};

const REQUIRED_MARKERS = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    "outside the shared `virtio_net` smoke-and-test route",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    "drivers/scsi/virtio_scsi.zig",
    "remain absent on current `master`",
    "rather than runtime queue, DMA, recovery, or throughput claims",
    "only the six-file `virtio_net` sextet may move through the shared wrapper set",
    "rollback-lab `virtio_scsi` survey-build packet",
    "stay outside that shared route until new checker-backed promotions land on `master`",
    "phase12_virtio_net_queue_resume.zig",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12_virtio_net_survey.zig",
};

const READINESS_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const CLOSURE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const PHASE12_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (READINESS_PATH) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE12_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
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
