const std = @import("std");

const RoadmapFeature = struct {
    feature: []const u8,
    status: []const u8,
    evidence: []const u8,
};

const RoadmapGap = struct {
    anchor: []const u8,
    required_features: []const RoadmapFeature,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    roadmap_gap: RoadmapGap,
};

fn expectFeature(
    features: []const RoadmapFeature,
    expected_feature: []const u8,
    expected_status: []const u8,
    expected_evidence_fragment: []const u8,
) !void {
    for (features) |feature| {
        if (std.mem.eql(u8, feature.feature, expected_feature)) {
            try std.testing.expectEqualStrings(expected_status, feature.status);
            try std.testing.expect(std.mem.indexOf(u8, feature.evidence, expected_evidence_fragment) != null);
            return;
        }
    }

    std.debug.print("missing roadmap feature: {s}\n", .{expected_feature});
    return error.MissingRoadmapFeature;
}

test "phase12 virtio scsi roadmap gap stays aligned with the survey note" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", manifest.anchor);
    try std.testing.expectEqualStrings(
        "Phase 12 complex production drivers and heavy helper consumers",
        manifest.roadmap_gap.anchor,
    );
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_gap.required_features.len);

    try expectFeature(
        manifest.roadmap_gap.required_features,
        "DMA-safe abstractions",
        "blocked_on_substrate",
        "DMA mapping",
    );
    try expectFeature(
        manifest.roadmap_gap.required_features,
        "queueing correctness",
        "bounded_planning_only",
        "queue-family planner",
    );
    try expectFeature(
        manifest.roadmap_gap.required_features,
        "throughput and recovery parity",
        "recovery_shape_only",
        "does not claim measured throughput",
    );
    try expectFeature(
        manifest.roadmap_gap.required_features,
        "segmented rollout",
        "active_survey_packet",
        "segmented across the bounded driver starter",
    );

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Roadmap Gap Versus Required Features") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "DMA-safe abstractions") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queueing correctness") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "throughput and recovery parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "segmented rollout") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still blocked") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "only partially covered") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "only shape-level evidence exists today") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current packet is intentionally segmented") != null);
}
