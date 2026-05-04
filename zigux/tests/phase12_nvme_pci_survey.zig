const std = @import("std");

const current_surveyed_commit = "8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1";

const SurveySummary = struct {
    nvme_pci_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_make_target_present: bool,
    preexisting_phase12_virtio_net_survey_present: bool,
    preexisting_phase12_virtio_net_starter_present: bool,
    preexisting_phase12_virtio_scsi_survey_present: bool,
    preexisting_phase12_virtio_scsi_starter_present: bool,
    nvme_pci_zig_present: bool,
    nvme_pci_test_present: bool,
    nvme_pci_slice_note_present: bool,
    nvme_pci_survey_gate_present: bool,
    nvme_pci_survey_note_present: bool,
    nvme_pci_raw_fallback_map_present: bool,
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

test "phase12 nvme pci survey manifest records the landed starter and remaining transport gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_nvme_pci_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", manifest.anchor);
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.nvme_pci_c_lines >= 4000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_starter_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_scsi_starter_present);
    try std.testing.expect(manifest.survey_summary.nvme_pci_zig_present);
    try std.testing.expect(manifest.survey_summary.nvme_pci_test_present);
    try std.testing.expect(manifest.survey_summary.nvme_pci_slice_note_present);
    try std.testing.expect(manifest.survey_summary.nvme_pci_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.nvme_pci_survey_note_present);
    try std.testing.expect(manifest.survey_summary.nvme_pci_raw_fallback_map_present);
    try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);

    const driver_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/nvme/host/pci.zig",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(driver_source);

    const driver_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_nvme_pci.zig",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(driver_tests);

    const phase12_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_build.zig",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(phase12_build);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-nvme-pci-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-nvme-pci-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const raw_fallback_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(raw_fallback_map);

    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub const IoQueueCountPlanSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub const PrpMetadataPlanSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub const DoorbellWindowSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn planIoQueueCount(") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn planPrpMetadata(") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn planDoorbellWindow(") != null);

    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase12 nvme pci io queue count helper negotiates controller and planner caps") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase12 nvme pci io queue count helper rejects empty negotiation and respects reset freeze") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase12 nvme pci prp metadata helper quantifies descriptor DMA footprint") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase12 nvme pci prp metadata helper respects reset freeze and resumes after reset") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase12 nvme pci doorbell window helper summarizes planned admin and io register aperture") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase12 nvme pci doorbell window helper tracks reset state without claiming live irq routing") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-nvme-pci-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-nvme-pci-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "test_step.dependOn(&run_phase12_nvme_pci_tests.step);") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "test_step.dependOn(&run_phase12_nvme_pci_survey_tests.step);") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "doorbell-window helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "PRP metadata helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "PRP-versus-SGL selection summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, current_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE_KEY=P12-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "packet-local verification head") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current `master` tip") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-nvme-pci-doorbell-window-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queue planner, doorbell-window helper, PRP buffer-shape helper, PRP metadata helper, and pointer-selection helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "historical-only evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fresh owner-lane replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "focused NVMe driver replay against live readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-nvme-pci-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-nvme-pci-tests 15 pass (15 total)") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-nvme-pci-raw-github-fallback-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current live starter now also carries one bounded doorbell-window helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Rollback And Reversible Delivery") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "owner: `NVMe PCI Lane`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback owner: `NVMe PCI Lane`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fallback path: keep `drivers/nvme/host/pci.c` as the source of truth") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queue planner plus queue-count, doorbell-window, PRP buffer-shape, PRP metadata helper, and pointer-selection helpers reviewable in isolation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback drill: run `make -C zigux phase12-validate`") != null);

    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "PHASE12_LANE_KEY=P12-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, current_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "It does not claim a live-head replay catalog.") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "## Tree Readback Roots") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "## Raw Pinned URLs") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "## Non-goals") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "The dedicated `zigux/tests/phase12_nvme_pci_survey.zig` gate reads this note back as part of the archived reviewability surface") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_doorbell_window = false;
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

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-doorbell-window-helper")) {
            saw_doorbell_window = true;
            try std.testing.expectEqualStrings("drivers/nvme/host/pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register aperture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset visibility") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "MSI-X vector wiring") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-live-queue-and-dma")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Host Memory Buffer") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blk-mq") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "doorbell-window helper") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_doorbell_window);
    try std.testing.expect(saw_blocker);
}
