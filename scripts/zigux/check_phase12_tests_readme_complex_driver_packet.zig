const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "TESTS_README_PATH",
    "SCRIPTS_README_PATH",
    "COMPLEX_DRIVER_NOTE_PATH",
    "RELEASE_READINESS_PATH",
    "BUILD_PATH",
    "MAKEFILE_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "COMPLEX_DRIVER_CHECKER_PATH",
    "CROSS_COMPILE_CHECKER_PATH",
    "RELEASE_READINESS_CHECKER_PATH",
    "LIBBPF_SNAPSHOT_CHECKER_PATH",
    "LIBBPF_LANE_MARKER_CHECKER_PATH",
    "LIBBPF_HEAVY_CONSUMER_CHECKER_PATH",
    "VALIDATOR_PATH",
    "WORKFLOW_PATH",
};

const TESTS_README_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "`scripts/zigux/check_build_only_phase12_surface.zig`",
    "`scripts/zigux/check_phase12_complex_driver_lane_packet.zig`",
    "`scripts/zigux/check_phase12_cross_compile_smoke.zig`",
    "`scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "`scripts/zigux/check_phase12_libbpf_snapshot.zig`",
    "`scripts/zigux/check_phase12_libbpf_lane_marker.zig`",
    "`scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`",
    "`scripts\zigux/validate_phase12.zig`",
    "`make -C zigux phase12-validate`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12-test`",
    "`make -C zigux phase12`",
    "`zigux/tests/phase12_virtio_net_queue_resume.zig`",
    "`zigux/tests/phase12_virtio_net_receive_refill_replay.zig`",
    "`zigux/tests/phase12_virtio_net_transmit_recycle.zig`",
    "`zigux/tests/phase12_virtio_net_post_reset_replay.zig`",
    "`zigux/tests/phase12_virtio_net_throughput_parity.zig`",
    "`zigux/tests/phase12_virtio_net_survey.zig`",
    "`zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "`zigux/tests/phase12_nvme_pci_manifest.json`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
};

const BUILD_MARKERS = [_][]const u8{
    "phase12_virtio_net_queue_resume.zig",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12_virtio_net_survey.zig",
    "phase12-virtio-net-queue-resume-tests",
    "phase12-virtio-net-receive-refill-replay-tests",
    "phase12-virtio-net-transmit-recycle-tests",
    "phase12-virtio-net-post-reset-replay-tests",
    "phase12-virtio-net-throughput-parity-tests",
    "phase12-virtio-net-survey-tests",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "run: zig run scripts/zigux/check_phase12_complex_driver_lane_packet.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase12_cross_compile_smoke.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "run: zig run scripts/zigux/validate_phase12.zig",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_TESTS_README_COMPLEX_DRIVER_PACKET",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
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
