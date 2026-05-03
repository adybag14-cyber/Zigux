const std = @import("std");

const SurveySummary = struct {
    virtio_ring_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_reset_reuse_test_present: bool,
    preexisting_virtio_ring_doc_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const RoadmapParityEvidenceEntry = struct {
    status: []const u8,
    evidence: []const []const u8,
};

const RoadmapParityEvidence = struct {
    virtqueue_wrappers: RoadmapParityEvidenceEntry,
    lab_only_driver_validation: RoadmapParityEvidenceEntry,
    dual_implementations_for_risky_areas: RoadmapParityEvidenceEntry,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    freeze_boundary_status: []const u8,
    risky_transport_posture: []const u8,
    roadmap_parity_evidence: RoadmapParityEvidence,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase10 virtio ring survey manifest records the live queue-discipline packet and parked MMIO blocker after landed interrupt-ack" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_ring_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const closure_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_closure_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(closure_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-ring-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const phase10_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase10_build);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const closure = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, closure_json, .{});
    defer closure.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P10-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |ch| {
        try std.testing.expect(std.ascii.isHex(ch));
    }
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", manifest.anchor);
    try std.testing.expectEqualStrings("aligned", manifest.freeze_boundary_status);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);
    try std.testing.expectEqualStrings("starter_landed", manifest.roadmap_parity_evidence.virtqueue_wrappers.status);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_parity_evidence.virtqueue_wrappers.evidence.len);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", manifest.roadmap_parity_evidence.virtqueue_wrappers.evidence[0]);
    try std.testing.expectEqualStrings("starter_landed", manifest.roadmap_parity_evidence.lab_only_driver_validation.status);
    try std.testing.expectEqual(@as(usize, 5), manifest.roadmap_parity_evidence.lab_only_driver_validation.evidence.len);
    try std.testing.expectEqualStrings("zigux/tests/phase10_build.zig", manifest.roadmap_parity_evidence.lab_only_driver_validation.evidence[0]);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.roadmap_parity_evidence.dual_implementations_for_risky_areas.status);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_parity_evidence.dual_implementations_for_risky_areas.evidence.len);
    try std.testing.expectEqualStrings("phase10-mmio-lifecycle-and-irq-paths", manifest.roadmap_parity_evidence.dual_implementations_for_risky_areas.evidence[0]);
    try std.testing.expect(manifest.survey_summary.virtio_ring_c_lines >= 3000);
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_reset_reuse_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);

    const required_ring_helpers = [_][]const u8{
        "phase10-virtqueue-shape-helper",
        "phase10-used-buffer-polling-helper",
        "phase10-callback-disable-helper",
        "phase10-callback-enable-helper",
        "phase10-callback-enable-prepare-helper",
        "phase10-callback-delay-helper",
        "phase10-notify-prepare-helper",
        "phase10-queue-reset-guard-helper",
        "phase10-queue-reset-helper",
        "phase10-broken-queue-recovery-helper",
    };
    for (required_ring_helpers) |gap_id| {
        const gap = findGap(manifest.gaps, gap_id) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("starter_landed", gap.status);
        try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
        try std.testing.expect(gap.why_now.len != 0);
    }

    const config_write_gap = findGap(manifest.gaps, "phase10-mmio-config-write-helper") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("starter_landed", config_write_gap.status);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", config_write_gap.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, config_write_gap.why_now, "config-write planning helper") != null);

    const blocked_mmio_gap = findGap(manifest.gaps, "phase10-mmio-lifecycle-and-irq-paths") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("blocked_on_risky_transport", blocked_mmio_gap.status);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", blocked_mmio_gap.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, blocked_mmio_gap.why_now, "interrupt acknowledgement") != null);
    try std.testing.expect(std.mem.indexOf(u8, blocked_mmio_gap.why_now, "probe or remove lifecycle") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_risky_transport")) {
            blocked_count += 1;
        }
    }
    try std.testing.expect(starter_landed_count >= 20);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);

    const landed_ring_helper_evidence = closure.value.object.get("landed_ring_helper_evidence") orelse return error.TestUnexpectedResult;
    const ring_helper_evidence = landed_ring_helper_evidence.object.get("zigux/tests/phase10_virtio_ring_manifest.json") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, required_ring_helpers.len), ring_helper_evidence.array.items.len);
    for (required_ring_helpers, 0..) |helper_id, index| {
        try std.testing.expectEqualStrings(helper_id, ring_helper_evidence.array.items[index].string);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_RING_ROADMAP_SCOREBOARD_ROWS=3") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_RING_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_RING_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_RING_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared closure evidence still owns the separate MMIO wrappers row") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-broken-queue-recovery-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-config-write-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-interrupt-ack-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Do not reopen the ring lane") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/*.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/kernel/") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "broken-queue recovery") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "phase10-mmio-lifecycle-and-irq-paths") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase10_build, "phase10_virtio_ring_reset_reuse.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase10_build, "phase10_virtio_ring_survey.zig") != null);
}
