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

test "phase12 nvme pci survey manifest records the landed starter surfaces and remaining roadmap gaps" {
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
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

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
    var saw_prp_metadata_helper = false;
    var saw_recovery_replay_helper = false;
    var saw_dma_transport_gap = false;
    var saw_throughput_recovery_gap = false;

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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recovery replay") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-driver-tests")) {
            saw_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "DMA page rounding") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP metadata helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recovery replay helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-nvme-pci-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP metadata helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recovery replay helper") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "segmented-rollout") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP helpers") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recovery replay helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-prp-shape-helper")) {
            saw_prp_shape_helper = true;
            try std.testing.expectEqualStrings("drivers/nvme/host/pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP buffer-shape helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rounded span") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP list bound checks") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-prp-metadata-helper")) {
            saw_prp_metadata_helper = true;
            try std.testing.expectEqualStrings("drivers/nvme/host/pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "command-inline data pointers") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "descriptor DMA footprint") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset-time descriptor rebuild") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-recovery-replay-helper")) {
            saw_recovery_replay_helper = true;
            try std.testing.expectEqualStrings("drivers/nvme/host/pci.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset-generation staleness") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "admin-queue replay need") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dropped I/O queue rebuild count") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "post-reset queue numbering") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-dma-safe-transport-gap")) {
            saw_dma_transport_gap = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-nvme-pci-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "DMA-safe abstractions") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Host Memory Buffer") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PRP metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "transport-safe substrate") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-nvme-pci-throughput-and-recovery-gap")) {
            saw_throughput_recovery_gap = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-nvme-pci-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_dma_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "throughput and recovery parity") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blk-mq queue_rq flow") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "IRQ-driven completion polling") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "timeout recovery plumbing") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 2), blocked_count);
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
    try std.testing.expect(saw_prp_metadata_helper);
    try std.testing.expect(saw_recovery_replay_helper);
    try std.testing.expect(saw_dma_transport_gap);
    try std.testing.expect(saw_throughput_recovery_gap);
}
