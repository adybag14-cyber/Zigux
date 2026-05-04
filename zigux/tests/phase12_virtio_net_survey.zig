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
    preexisting_phase12_virtio_net_syntax_lab_present: bool,
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
        std.mem.eql(u8, status, "blocked_on_dma_transport");
}

fn isLowerHexCommit(value: []const u8) bool {
    if (value.len != 40) return false;

    for (value) |byte| {
        switch (byte) {
            '0'...'9', 'a'...'f' => {},
            else => return false,
        }
    }

    return true;
}

test "phase12 virtio_net survey manifest stays aligned with the landed probe starter" {
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

    const syntax_lab_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_net_syntax_lab.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(syntax_lab_file);

    const direct_test_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_net.zig",
        std.testing.allocator,
        .limited(96 * 1024),
    );
    defer std.testing.allocator.free(direct_test_file);

    const driver_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/net/virtio_net.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(driver_file);

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
    try std.testing.expectEqualStrings("P12-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", manifest.anchor);
    try std.testing.expectEqualStrings("bc2373f7deedf021c73beaae29555a9ac6b0536d", manifest.surveyed_commit);
    try std.testing.expect(isLowerHexCommit(manifest.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_net_c_lines >= 7000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_zig_present);
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12_virtio_net_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12_virtio_net_tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "run_phase12_virtio_net_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12_virtio_net_syntax_lab_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase12-virtio-net-syntax-lab-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "run_phase12_virtio_net_syntax_lab_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "const virtio_net = @import(\"virtio_net\");") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.ModuleDescriptor") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.RecoveryAction") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.QueueFallbackReason") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.RssSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.ProbeRequest") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.ProbeSnapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.QueueRecoverySummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.QueueResumeSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "virtio_net.ReceiveQueueRefillPath") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "ReceiveQueueRefillPath.recycled_room_reuse") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "ReceiveQueueRefillPath.fresh_allocation") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "VirtioNetProbeLab.descriptor()") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "QueueResumeScope.data_control_and_rss") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "HeaderShape.hash_report_tunnel") != null);
    try std.testing.expect(std.mem.indexOf(u8, syntax_lab_file, "MergeableReceiveRefillSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "test \"phase12 virtio net restore clears stale refill planning state\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "planMergeableReceiveRefill(4)") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "error.ProbeSnapshotUnavailable") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "ReceiveQueueRefillPath.recycled_room_reuse") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "ReceiveQueueRefillPath.fresh_allocation") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "recycled_room_bytes") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "fresh_allocation_bytes") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "packet_budget_bytes") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_test_file, "min_buf_len_bytes") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_core_foundation = false;
    var saw_ring_foundation = false;
    var saw_survey_gate = false;
    var saw_survey_note = false;
    var saw_probe_starter = false;
    var saw_ready_next = false;
    var saw_hdr_len_followup = false;
    var saw_recovery_summary = false;
    var saw_resume_summary = false;
    var saw_receive_path_summary = false;
    var saw_mergeable_refill_summary = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_dma_transport")) {
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

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-probe-snapshot-starter")) {
            saw_probe_starter = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtnet_probe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "RSS") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-queue-recovery-followup")) {
            saw_ready_next = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue recovery action") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-pair clamps") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "single-queue fallback") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-hdr-len-followup")) {
            saw_hdr_len_followup = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`hdr_len`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "UDP-tunnel") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-queue-recovery-summary")) {
            saw_recovery_summary = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freezes") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "restore") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-queue-resume-summary")) {
            saw_resume_summary = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resume immediately") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "RSS") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "restore clears stale refill planning state") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fresh probe snapshot") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-receive-path-summary")) {
            saw_receive_path_summary = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "big-packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`any_header_sg`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "XDP") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-mergeable-refill-summary")) {
            saw_mergeable_refill_summary = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "packet budget bytes") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "minimum buffer length") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "required headroom") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recycled room reuse") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fresh allocation bytes") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-runtime-data-path")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_net_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "NAPI poll loops") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "XDP or XSK") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queueing substrate") != null);
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
    try std.testing.expect(saw_probe_starter);
    try std.testing.expect(saw_ready_next);
    try std.testing.expect(saw_hdr_len_followup);
    try std.testing.expect(saw_recovery_summary);
    try std.testing.expect(saw_resume_summary);
    try std.testing.expect(saw_receive_path_summary);
    try std.testing.expect(saw_mergeable_refill_summary);
    try std.testing.expect(saw_blocker);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.lane_key) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "probe snapshot helper plus matching queue-recovery, queue-resume, `hdr_len`, receive-path, and mergeable-refill summaries") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queue-recovery summary follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queue-resume summary follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded receive-path follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded mergeable-refill follow-up") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "syntax-lab compile smoke") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-virtio-net-syntax-lab-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "descriptor, request, snapshot, queue-recovery, queue-resume, and refill review types") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still-blocked `phase12-virtio-net-runtime-data-path`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase12_virtio_net_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "first rollback and drift check before broader shared Phase 12 validation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "build-graph-only compile-smoke proof") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recycled-room reuse, and fresh-allocation bytes") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "restore clears stale refill planning state") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fresh probe snapshot") != null);

    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub const VirtioNetProbeLab = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub fn captureProbeSnapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub fn freezeForRecovery") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub fn restoreAfterRecovery") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub fn planQueueResume") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub fn planMergeableReceiveRefill") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "pub const MergeableReceiveRefillSummary = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "recycled_room_bytes") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_file, "fresh_allocation_bytes") != null);
}
