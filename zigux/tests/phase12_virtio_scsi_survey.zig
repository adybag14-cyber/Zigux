const std = @import("std");

const SurveySummary = struct {
    virtio_scsi_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_make_target_present: bool,
    preexisting_phase12_virtio_net_survey_present: bool,
    preexisting_phase12_nvme_pci_starter_present: bool,
    preexisting_phase12_virtio_scsi_survey_present: bool,
    preexisting_phase12_survey_note_present: bool,
    preexisting_virtio_scsi_zig_present: bool,
    preexisting_phase12_virtio_scsi_test_present: bool,
    preexisting_phase12_virtio_scsi_slice_note_present: bool,
    preexisting_phase12_raw_github_fallback_catalog_present: bool,
    raw_github_tree_fallback_count: usize,
    raw_github_file_fallback_count: usize,
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

test "phase12 virtio_scsi survey manifest records the landed host-limit summary starter" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const phase12_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase12_build);

    const virtio_scsi_driver = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/scsi/virtio_scsi.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(virtio_scsi_driver);

    const virtio_scsi_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_virtio_scsi.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(virtio_scsi_tests);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const raw_fallback_catalog = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(raw_fallback_catalog);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", manifest.anchor);
    try std.testing.expectEqualStrings("ec1f21e06c76ffea564156593196096c803a53e4", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_scsi_c_lines >= 1000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_nvme_pci_starter_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_scsi_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_raw_github_fallback_catalog_present);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.raw_github_tree_fallback_count);
    try std.testing.expectEqual(@as(usize, 10), manifest.survey_summary.raw_github_file_fallback_count);
    try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-validate:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12: phase12-validate phase12-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "probe snapshot of `virtscsi_probe()` config fields") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "host-limit summary helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "now also lands one tiny host-limit summary helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`scsi_host_alloc()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`scsi_add_host()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`scsi_scan_host()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queue-layout, recovery, probe snapshot, and host-limit summary starters") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-virtio-scsi-raw-github-fallback-catalog.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ec1f21e06c76ffea564156593196096c803a53e4") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ready-next `phase12-virtio-scsi-host-limit-summary-followup`") == null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "transport freeze or restore boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "synthetic `can_queue`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "`cmd_per_lun`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "`nr_hw_queues`") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "verified_master_head: `ec1f21e06c76ffea564156593196096c803a53e4`") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "raw_github_tree_fallback_count: `3`") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "raw_github_file_fallback_count: `10`") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/drivers/scsi/virtio_scsi.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/zigux/tests/phase12_virtio_scsi_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "1c90a3ecd974fa486b5cd2569063341ac5a10a557d4fd5c85916bb6c49f9c607") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/scripts/zigux/validate-phase12.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "6813189c32aae8c7c7bb14799d8eff22fe36c842cf2134e3125fc8463c5f2a24") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/zigux/Makefile") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "761ed2df3cd21b0de60124c3d341dc8bf19dc21f982656005f941222becf8b00") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_scsi_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_scsi_tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_scsi_survey_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_scsi_survey_tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "run_phase12_virtio_scsi_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, virtio_scsi_driver, "pub const VirtioScsiQueueLab = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, virtio_scsi_driver, "provides_probe_config_snapshot = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, virtio_scsi_driver, "provides_host_limit_summary = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, virtio_scsi_driver, "pub fn captureProbeSnapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, virtio_scsi_driver, "pub fn captureHostLimitSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, virtio_scsi_tests, "phase12 virtio scsi probe snapshot records config fields and queue layout") != null);
    try std.testing.expect(std.mem.indexOf(u8, virtio_scsi_tests, "phase12 virtio scsi host limit summary clamps cmd_per_lun against synthetic can_queue") != null);

    var starter_landed_count: usize = 0;
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
    var saw_raw_fallback_catalog = false;
    var saw_probe_snapshot = false;
    var saw_host_limit_summary = false;
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
        }

        if (std.mem.eql(u8, gap.id, "phase12-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "make target") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bounded driver test lane") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "host-limit summary helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-scsi-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-raw-github-fallback-catalog")) {
            saw_raw_fallback_catalog = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "three public tree entry points") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ten commit-pinned raw GitHub artifact URLs") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sha256 hashes") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-probe-config-snapshot-starter")) {
            saw_probe_snapshot = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landed probe snapshot helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtscsi_probe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "request virtqueue layout") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-host-limit-summary-starter")) {
            saw_host_limit_summary = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "host-limit summary helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "synthetic `can_queue`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`nr_hw_queues`") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-runtime-queues-and-scan")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "scsi_add_host()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blk-mq") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "host-limit summary helper is now landed") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
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
    try std.testing.expect(saw_raw_fallback_catalog);
    try std.testing.expect(saw_probe_snapshot);
    try std.testing.expect(saw_host_limit_summary);
    try std.testing.expect(saw_blocker);
}
