const std = @import("std");

const SurveySummary = struct {
    virtio_net_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_input_zig_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_virtio_net_survey_present: bool,
    preexisting_phase12_survey_note_present: bool,
    preexisting_virtio_net_zig_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_dma_transport");
}

test "phase12 virtio_net survey manifest stays aligned with the landed driver packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_net_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-net-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", manifest.anchor);
    try std.testing.expectEqualStrings("7361ac51374149a96b7a7a2c6ea3c995d8cc1231", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_net_c_lines >= 7000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_zig_present);
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12_virtio_net_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12_virtio_net_tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12_virtio_net_syntax_lab_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12_virtio_net_syntax_lab_tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "run_phase12_virtio_net_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "run_phase12_virtio_net_syntax_lab_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "segmented rollout boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runtime-data-path boundary remains blocked") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-virtio-net-segmented-rollout-boundary") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_core_foundation = false;
    var saw_ring_foundation = false;
    var saw_survey_gate = false;
    var saw_survey_note = false;
    var saw_syntax_lab = false;
    var saw_probe_starter = false;
    var saw_queue_recovery = false;
    var saw_receive_refill = false;
    var saw_transmit_recycle = false;
    var saw_mergeable_buffer_length = false;
    var saw_segmented_rollout_boundary = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {} else if (std.mem.eql(u8, gap.status, "blocked_on_dma_transport")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_build.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "direct probe-starter gate") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-core-foundation")) {
            saw_core_foundation = true;
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "feature negotiation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "descriptor-shape metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notification accounting") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-ring-foundation")) {
            saw_ring_foundation = true;
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-shape") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notification bookkeeping") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "callback-enable") == null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_net_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "build wiring") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-net-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-syntax-lab-gate")) {
            saw_syntax_lab = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_net_syntax_lab.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "direct syntax-lab gate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bounded probe exports") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-probe-snapshot-starter")) {
            saw_probe_starter = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtnet_probe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "RSS") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-queue-recovery-followup")) {
            saw_queue_recovery = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-recovery") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rebuild scope") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-receive-refill-followup")) {
            saw_receive_refill = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "mergeable-buffer headroom") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fresh probe replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "RSS-aware refill") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "clamp-versus-single-queue recovery intent") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-transmit-recycle-followup")) {
            saw_transmit_recycle = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "completion-side queue-reuse step") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "control-virtqueue restore ordering") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "receive-refill coordination") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-mergeable-buffer-length-summary")) {
            saw_mergeable_buffer_length = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`get_mergeable_buf_len()`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "observed average packet size") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "minimum floor") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "page payload") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "page-minus-room") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`skb_shared_info`") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-segmented-rollout-boundary")) {
            saw_segmented_rollout_boundary = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-net-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "segmented rollout") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "mergeable-buffer-length") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runtime data path remains blocked") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-runtime-data-path")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_net_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "page_pool DMA") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "XDP") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 13), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_core_foundation);
    try std.testing.expect(saw_ring_foundation);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_syntax_lab);
    try std.testing.expect(saw_probe_starter);
    try std.testing.expect(saw_queue_recovery);
    try std.testing.expect(saw_receive_refill);
    try std.testing.expect(saw_transmit_recycle);
    try std.testing.expect(saw_mergeable_buffer_length);
    try std.testing.expect(saw_segmented_rollout_boundary);
    try std.testing.expect(saw_blocker);

    const driver_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/net/virtio_net.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(driver_file);

    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub const MergeableBufferLengthSummary = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub fn planMergeableBufferLength") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "fn summarizeMergeableBufferLength(") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "mergeable-buffer-length follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "page-minus-room") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`skb_shared_info`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ready-next `phase12-virtio-net-mergeable-buffer-length-summary`") == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_note,
        "does not ship a separate `Documentation/zigux/phase12-virtio-net-slice.md`",
    ) != null);
}
