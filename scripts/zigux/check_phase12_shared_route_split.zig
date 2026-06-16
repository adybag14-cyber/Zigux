const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "NOTE_PATH",
    "VIRTIO_NET_SURVEY_PATH",
    "NVME_SURVEY_PATH",
    "VIRTIO_SCSI_SURVEY_PATH",
    "BUILD_PATH",
    "INVENTORY_PATH",
    "NVME_BUILD_PATH",
    "VIRTIO_SCSI_BUILD_PATH",
};

const EXPECTED_BUILD_TEST_NAMES = [_][]const u8{
    "phase12-virtio-net-queue-resume-tests",
    "phase12-virtio-net-transmit-recycle-tests",
    "phase12-virtio-net-receive-refill-replay-tests",
    "phase12-virtio-net-post-reset-replay-tests",
    "phase12-virtio-net-throughput-parity-tests",
    "phase12-virtio-net-survey-tests",
};

const EXPECTED_SHARED_DEP_STEPS = [_][]const u8{
    "run_virtio_net_queue_resume_tests",
    "run_virtio_net_transmit_recycle_tests",
    "run_virtio_net_receive_refill_replay_tests",
    "run_virtio_net_post_reset_replay_tests",
    "run_virtio_net_throughput_parity_tests",
    "run_virtio_net_survey_tests",
};

const TEXT_MARKERS = [_][]const u8{
    "split-helper `virtio_net` packet",
    "while leaving it outside the shared smoke-first route.",
    "queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
    "the standalone syntax-lab companion remains compile-smoke evidence beside that sextet",
    "the shared `zigux/tests/phase12_build.zig` route still stays virtio-net-only",
    "the bounded NVMe packet remains driver-local through the dedicated `phase12-nvme-pci-direct-test` route",
    "the dedicated `phase12-nvme-pci-survey-test` route",
    "the dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route now reruns the rollback-only survey packet directly",
    "the shared `zigux/tests/phase12_build.zig` route still covers only the `virtio_net` queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate tests",
    "phase12_virtio_net_queue_resume.zig",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12_virtio_net_survey.zig",
    "phase12-virtio-net-throughput-parity",
    "phase12-nvme-pci-direct-test",
    "phase12-nvme-pci-verify-test",
    "phase12-nvme-pci-replay-wrapper-test",
    "phase12-virtio-scsi-survey-tests",
    "rollback-only survey tests",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_SHARED_ROUTE_SPLIT",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BUILD_TEST_NAMES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SHARED_DEP_STEPS) |marker| try guard.requireMarker(text, marker);
    for (TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CHECK_NAME) |marker| try guard.requireMarker(text, marker);
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
