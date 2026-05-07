const std = @import("std");

const RoadmapGapEntry = struct {
    required_by_roadmap: bool,
    status: []const u8,
    current_surface: []const u8,
    blocked_by: []const u8,
};

const RoadmapGapCheck = struct {
    dma_safe_abstractions: RoadmapGapEntry,
    queueing_correctness: RoadmapGapEntry,
    throughput_and_recovery_parity: RoadmapGapEntry,
    segmented_rollout: RoadmapGapEntry,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    roadmap_gap_check: RoadmapGapCheck,
};

fn isAllowedGapStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "blocked") or
        std.mem.eql(u8, status, "bounded_starter_only") or
        std.mem.eql(u8, status, "review_boundary_landed");
}

test "phase12 virtio net roadmap gap check stays machine-checkable" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_net_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);

    const gap = manifest.roadmap_gap_check;
    try std.testing.expect(gap.dma_safe_abstractions.required_by_roadmap);
    try std.testing.expect(gap.queueing_correctness.required_by_roadmap);
    try std.testing.expect(gap.throughput_and_recovery_parity.required_by_roadmap);
    try std.testing.expect(gap.segmented_rollout.required_by_roadmap);

    try std.testing.expect(isAllowedGapStatus(gap.dma_safe_abstractions.status));
    try std.testing.expect(isAllowedGapStatus(gap.queueing_correctness.status));
    try std.testing.expect(isAllowedGapStatus(gap.throughput_and_recovery_parity.status));
    try std.testing.expect(isAllowedGapStatus(gap.segmented_rollout.status));

    try std.testing.expectEqualStrings("blocked", gap.dma_safe_abstractions.status);
    try std.testing.expect(std.mem.indexOf(u8, gap.dma_safe_abstractions.current_surface, "probe snapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.dma_safe_abstractions.current_surface, "mergeable-buffer-length planning") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.dma_safe_abstractions.blocked_by, "DMA-safe buffer ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.dma_safe_abstractions.blocked_by, "page_pool") != null);

    try std.testing.expectEqualStrings("bounded_starter_only", gap.queueing_correctness.status);
    try std.testing.expect(std.mem.indexOf(u8, gap.queueing_correctness.current_surface, "queue-pair counts") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.queueing_correctness.current_surface, "control-virtqueue presence") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.queueing_correctness.blocked_by, "virtqueue submission") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.queueing_correctness.blocked_by, "NAPI-backed") != null);

    try std.testing.expectEqualStrings("bounded_starter_only", gap.throughput_and_recovery_parity.status);
    try std.testing.expect(std.mem.indexOf(u8, gap.throughput_and_recovery_parity.current_surface, "mergeable-buffer sizing") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.throughput_and_recovery_parity.current_surface, "RSS restore ordering") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.throughput_and_recovery_parity.blocked_by, "throughput evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.throughput_and_recovery_parity.blocked_by, "runtime recovery replay") != null);

    try std.testing.expectEqualStrings("review_boundary_landed", gap.segmented_rollout.status);
    try std.testing.expect(std.mem.indexOf(u8, gap.segmented_rollout.current_surface, "queue-recovery") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.segmented_rollout.current_surface, "mergeable-buffer-length") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.segmented_rollout.blocked_by, "XDP or XSK execution") != null);
    try std.testing.expect(std.mem.indexOf(u8, gap.segmented_rollout.blocked_by, "net_device lifecycle work") != null);
}
