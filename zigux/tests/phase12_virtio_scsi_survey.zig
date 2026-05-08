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
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);

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
    var saw_event_rearm = false;
    var saw_event_buffer_ownership = false;
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recovery event-rearm summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "event-buffer ownership summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fallback path") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reversible-delivery drill") != null);
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

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-recovery-event-rearm-summary-starter")) {
            saw_event_rearm = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reusing the frozen event queue index") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "device ready before rearm") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "request queue reuse") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-recovery-event-buffer-ownership-summary-starter")) {
            saw_event_buffer_ownership = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "event queue reserved during freeze") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "request queues from borrowing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "restore rearm after device ready") != null);
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

    try std.testing.expectEqual(@as(usize, 14), starter_landed_count);
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
    try std.testing.expect(saw_event_rearm);
    try std.testing.expect(saw_event_buffer_ownership);
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
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "owner lane: `P12-L13`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-virtio-scsi-raw-github-fallback-catalog.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "does not own the active survey packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "restore queue rebind summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recovery event-rearm summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "event-buffer ownership summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Rollback and Reversible Delivery") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback owner:") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fallback path:") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reversible-delivery evidence:") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback drill:") != null);
}

test "phase12 virtio_scsi slice note keeps the rollback drill explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const expected_fragments = [_][]const u8{
        "records the fixed event-buffer fanout used by the driver and derives one bounded restore-time event-buffer ownership summary",
        "freezes queue planning and event recycling intent across a lab-only transport freeze or restore boundary",
        "clears the old queue snapshot so the next step must replan",
        "derives one bounded restore-sequencing summary from the frozen queue layout",
        "`virtscsi_restore()` calling `find_vqs`, `virtio_device_ready()`, and event rearm",
        "records one bounded recovery event-rearm summary from the frozen queue layout",
        "device-ready-before-rearm rule",
        "without pretending to re-run `scsi_scan_host()`",
    };

    for (expected_fragments) |fragment| {
        try expectContains(slice_note, fragment);
    }
}

test "phase12 virtio scsi raw fallback catalog stays aligned with the shipped build-only replay surface" {
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
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-slice.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-survey.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-raw-github-coverage-survey.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-closure-checklist.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-coordination-matrix.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/README.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_build.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_survey.zig",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_manifest.json",
        "https://github.com/adybag14-cyber/Zigux/blob/master/scripts/zigux/README.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/README.md",
        "https://github.com/adybag14-cyber/Zigux/blob/master/zigux/Makefile",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/scsi/virtio_scsi.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-slice.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-survey.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-raw-github-coverage-survey.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-closure-checklist.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-coordination-matrix.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/README.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_build.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_survey.zig",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_manifest.json",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/scripts/zigux/README.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/README.md",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/Makefile",
        "- current virtio_scsi smoke packet surfaces: `zigux/tests/phase12_virtio_scsi.zig` and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
        "2. `make -C zigux phase12-smoke`",
        "3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
        "4. `make -C zigux phase12`",
        "Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether those same shipped surfaces are close enough to describe the active Phase 12 tranche as release-closed.",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md` should stay visible beside this fallback catalog and the compact release coordination matrix",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md` should stay visible beside this fallback catalog so the two commit-pinned artifacts plus two shared-tree-only anchors split remains reviewable without turning this driver-local note into a broader fallback-ownership summary.",
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback catalog, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback catalog into a second sequencing document.",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` reruns that checker so this fallback wording stays aligned with the shipped PMO release packet.",
        "This catalog should stay read-only and should not be used to imply an unshipped `validate-phase12.py`, any `check-phase12-*.py` packet, or a `make -C zigux phase12-validate` target.",
    };

    for (expected_fragments) |fragment| {
        try expectContains(catalog, fragment);
    }

    try std.testing.expectEqual(
        @as(usize, 1),
        std.mem.count(u8, catalog, "- current virtio_scsi smoke packet surfaces: `zigux/tests/phase12_virtio_scsi.zig` and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`"),
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        std.mem.count(u8, catalog, "1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`"),
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        std.mem.count(u8, catalog, "2. `make -C zigux phase12-smoke`"),
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        std.mem.count(u8, catalog, "3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`"),
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        std.mem.count(u8, catalog, "4. `make -C zigux phase12`"),
    );
}

test "phase12 virtio scsi shared release packet keeps rollback evidence explicit across PMO surfaces" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const release_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-release-sequencing.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(release_note);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const closure_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-release-closure-checklist.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(closure_checklist);

    const release_readiness = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-release-readiness-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(release_readiness);

    const coordination_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-release-coordination-matrix.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(coordination_matrix);

    const release_fragments = [_][]const u8{
        "The current storage-lane rollback drill is a bounded `virtio_scsi` lab surface, not a tranche-wide recovery claim.",
        "`Documentation/zigux/phase12-virtio-scsi-slice.md` now records a lab-only freeze or restore boundary",
        "reversible-delivery scaffolding",
        "the bounded storage rollback drill is reviewable release evidence",
    };

    for (release_fragments) |fragment| {
        try expectContains(release_note, fragment);
    }

    const checklist_fragments = [_][]const u8{
        "`Documentation/zigux/phase12-virtio-scsi-slice.md`",
        "`Documentation/zigux/phase12-virtio-scsi-survey.md`",
        "`zigux/tests/phase12_virtio_scsi.zig`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_manifest.json`",
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
        "`make -C zigux phase12-smoke`",
        "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
        "`make -C zigux phase12`",
    };

    for (checklist_fragments) |fragment| {
        try expectContains(review_checklist, fragment);
    }

    const closure_fragments = [_][]const u8{
        "The bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill must remain described as lab-only reversible-delivery evidence rather than closure-ready runtime recovery.",
        "Queueing, throughput, rollback, and recovery wording must keep the freeze-map split explicit: this packet can describe bounded driver-local evidence and the lab-only `virtio_scsi` rollback drill, but it must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.",
    };

    for (closure_fragments) |fragment| {
        try expectContains(closure_checklist, fragment);
    }

    const release_readiness_fragments = [_][]const u8{
        "the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback-drill wording",
        "The bounded `virtio_scsi` rollback drill remains storage-lane-local release evidence, not a tranche-wide recovery claim.",
    };

    for (release_readiness_fragments) |fragment| {
        try expectContains(release_readiness, fragment);
    }

    const coordination_fragments = [_][]const u8{
        "the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill remains lab-only reversible-delivery evidence inside this active packet",
        "`Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill still reads as lab-only reversible-delivery evidence rather than tranche-wide runtime recovery or release-closed proof",
    };

    for (coordination_fragments) |fragment| {
        try expectContains(coordination_matrix, fragment);
    }
}
