const std = @import("std");

const SurveySummary = struct {
    virtio_scsi_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_virtio_net_survey_present: bool,
    preexisting_phase12_nvme_pci_starter_present: bool,
    preexisting_phase12_virtio_scsi_survey_present: bool,
    preexisting_phase12_survey_note_present: bool,
    preexisting_virtio_scsi_zig_present: bool,
    preexisting_phase12_virtio_scsi_test_present: bool,
    preexisting_phase12_virtio_scsi_slice_note_present: bool,
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase12 virtio_scsi survey manifest records the landed queue starter and probe snapshot helper" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", manifest.anchor);
    try std.testing.expectEqualStrings("ee64eec272a352da1d967999c99bb3c3560c9b97", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_scsi_c_lines >= 1000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_nvme_pci_starter_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_scsi_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_slice_note_present);
    try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_core_foundation = false;
    var saw_ring_foundation = false;
    var saw_survey_gate = false;
    var saw_survey_note = false;
    var saw_driver_starter = false;
    var saw_driver_tests = false;
    var saw_slice_note = false;
    var saw_probe_snapshot = false;
    var saw_restore_queue_rebind = false;
    var saw_recovery_rollback = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_dma_transport")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_build.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "DMA-backed") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-scsi-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-driver-starter")) {
            saw_driver_starter = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "control, event, request, and request_poll") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blocks planning while transport is frozen") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "clears queue state after restore") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poll-queue clamping") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "global virtqueue indexes") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe-config snapshot") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-scsi-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-probe-config-snapshot-starter")) {
            saw_probe_snapshot = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtscsi_probe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "num_queues") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "max_target") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-restore-queue-rebind-summary-starter")) {
            saw_restore_queue_rebind = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtscsi_restore()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "default versus poll queue ranges") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "event buffers until after device ready") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-recovery-rollback-summary-starter")) {
            saw_recovery_rollback = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "keeps the frozen queue layout available for restore") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blocks queue planning and request access until restore") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "requires replanning before queue reuse") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-runtime-queues-and-scan")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "scsi_add_host()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blk-mq") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_core_foundation);
    try std.testing.expect(saw_ring_foundation);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_driver_starter);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_probe_snapshot);
    try std.testing.expect(saw_restore_queue_rebind);
    try std.testing.expect(saw_recovery_rollback);
    try std.testing.expect(saw_blocker);
}

test "phase12 virtio_scsi survey note keeps the active lane identity and fallback role explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE=P12-L13") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-virtio-scsi-raw-github-fallback-catalog.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "does not own the active survey packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "restore queue rebind summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback summary") != null);
}

test "phase12 virtio_scsi raw fallback catalog stays aligned with the shipped build-only replay surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const catalog = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(catalog);

    const expected_fragments = [_][]const u8{
        "`PHASE12_STATUS=active`",
        "`active_survey_lane: P12-L13`",
        "`historical_fallback_lane: P12-L09`",
        "`PHASE12_SLICE=virtio-scsi-raw-github-fallback-catalog`",
        "https://github.com/adybag14-cyber/Zigux/blob/master/drivers/scsi/virtio_scsi.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-survey.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_build.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_survey.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_manifest.json",
        "https://github.com/adybag14-cyber/Zigux/blob/master/scripts/zigux/README.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/README.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/Makefile",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/scsi/virtio_scsi.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-survey.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_build.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_survey.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_manifest.json",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/scripts/zigux/README.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/README.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/Makefile",
        "1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
        "2. `make -C zigux phase12-smoke`",
        "3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
        "4. `make -C zigux phase12`",
        "This catalog should stay read-only and should not be used to imply an unshipped `validate-phase12.py`, any `check-phase12-*.py` packet, or a `make -C zigux phase12-validate` target.",
    };

    for (expected_fragments) |fragment| {
        try expectContains(catalog, fragment);
    }
}
