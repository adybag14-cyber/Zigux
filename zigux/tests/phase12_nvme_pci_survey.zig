const std = @import("std");

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

test "phase12 nvme pci survey manifest records the landed starter surfaces and remaining transport gap" {
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
    try std.testing.expectEqualStrings("P12-Y02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", manifest.anchor);
    try std.testing.expectEqualStrings("f7d8ad3bf36fd42ee03b041bbf1bbbb7dccc6200", manifest.surveyed_commit);
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
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_tests = false;
    var saw_slice_note = false;
    var saw_virtio_net_starter = false;
    var saw_virtio_scsi_starter = false;
    var saw_survey_gate = false;
    var saw_survey_note = false;
    var saw_prp_shape_helper = false;
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

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-driver-starter")) {
            saw_starter = true;
            try std.testing.expectEqualStrings("drivers/nvme/host/pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue planner") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "doorbell offsets") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-driver-tests")) {
            saw_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "DMA page rounding") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-nvme-pci-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-driver-starter")) {
            saw_virtio_net_starter = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe snapshot starter") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-driver-starter")) {
            saw_virtio_scsi_starter = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-layout starter") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-nvme-pci-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-prp-shape-helper")) {
            saw_prp_shape_helper = true;
            try std.testing.expectEqualStrings("drivers/nvme/host/pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP buffer-shape helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rounded span") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP list bound checks") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-live-queue-and-dma")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Host Memory Buffer") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blk-mq") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "roadmap-approved DMA-safe transport substrate") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 10), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_virtio_net_starter);
    try std.testing.expect(saw_virtio_scsi_starter);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_prp_shape_helper);
    try std.testing.expect(saw_blocker);
}

test "phase12 nvme pci survey packet records the active ownership lane and blocked transport boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const driver_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/nvme/host/pci.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(driver_source);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-nvme-pci-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-nvme-pci-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const fallback_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(fallback_map);

    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub const OwnershipBoundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub const OwnershipSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn ownershipSummary() OwnershipSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".owner_lane = \"P12-Y02\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".live_dma_owner = .dma_transport_substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".recovery_transport_owner = .dma_transport_substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE_KEY=P12-Y02") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "owner lane: `P12-Y02`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "blocked DMA and recovery transport work remains owned by the broader Phase 12 transport substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "Ownership boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "`P12-Y02` owns only the queue-planning and PRP-shape starter surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_map, "PHASE12_LANE_KEY=P12-Y02") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_map, "active owner lane: `P12-Y02`") != null);
}
