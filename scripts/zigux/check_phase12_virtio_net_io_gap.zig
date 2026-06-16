const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_NET_IO_GAP_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_net_survey.zig",
};

const ABSENT_FILES = [_][]const u8{
    "drivers/net/virtio_net.zig",
    "zigux/tests/phase12_virtio_net.zig",
};

const SURVEY_MARKERS = [_][]const u8{
    "PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only",
    "the packet still does not claim live DMA-safe receive ownership",
    "smoke still runs through the direct build-file command",
    "explicit receive-refill and transmit-recycle readiness booleans",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"lane_key\": \"P12-L04\"",
    "\"phase\": \"Phase 12\"",
    "\"verified_on\": \"2026-05-25\"",
    "\"status\": \"split_helper_packet_present_runtime_data_path_blocked\"",
    "\"status\": \"split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present\"",
    "\"status\": \"throughput_parity_helper_present_review_only_runtime_completion_missing\"",
    "\"status\": \"split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete\"",
    "\"id\": \"phase12-virtio-net-runtime-data-path\"",
    "\"status\": \"blocked_on_dma_transport_runtime\"",
    "live DMA-safe receive ownership",
    "page-pool wiring",
    "transport-backed submit flow",
    "interrupt-backed completion handling",
};

const SURVEY_GATE_MARKERS = [_][]const u8{
    "phase12 virtio net survey manifest tracks the shared-build survey-gate coverage truthfully",
    "phase12 virtio net survey note reflects the shared survey-gate route",
    "phase12 virtio net survey gate keeps the present files and shared routes explicit",
    "try std.testing.expect(!try pathExists(\"drivers/net/virtio_net.zig\"));",
    "try std.testing.expect(!try pathExists(\"zigux/tests/phase12_virtio_net.zig\"));",
};

const HELPER_MARKERS = [_][]const u8{
    "drivers/net/virtio_net_queue_resume.zig",
    "receive_submission_owner",
    "transmit_submission_owner",
    "control_queue_restore",
    "probe_snapshot_replay",
    "can_resume_queues",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "descriptors_pending_repost",
    ".descriptor_repost",
    "replay_ready",
    "queue_pairs_preserved",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "CompletedOwnershipDisposition",
    "returns_completed_ownership_to_driver",
    ".wake_queue",
    "free_descriptors_after",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "PostResetReplayCheckpoint",
    "after_probe_snapshot_replay",
    "resumes_receive_submission",
    "queues_ready_for_driver_ownership",
    "drivers/net/virtio_net_throughput_parity.zig",
    "needs_post_reset_probe_replay",
    "receive_refill_ready",
    "transmit_recycle_ready",
    "throughput_ratio_pct",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_FILES) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
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
