const std = @import("std");

const SurveySummary = struct {
    virtio_mmio_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_doc_present: bool,
    preexisting_virtio_ring_survey_present: bool,
    preexisting_virtio_input_zig_present: bool,
    preexisting_virtio_input_test_present: bool,
    preexisting_virtio_input_survey_present: bool,
    preexisting_virtio_mmio_zig_present: bool,
    preexisting_virtio_mmio_test_present: bool,
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
    freeze_map: []const u8,
    freeze_boundary_status: []const u8,
    freeze_status_change_claimed: bool,
    risky_transport_posture: []const u8,
    allowed_evidence_kinds: []const []const u8,
    forbidden_transport_claims: []const []const u8,
    architecture_council_reopen_required: bool,
    architecture_council_reopen_attached: bool,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_risky_transport");
}

test "phase10 virtio mmio survey manifest records the landed identity-backed packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-mmio-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P10-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", manifest.anchor);
    try std.testing.expectEqualStrings("84f90e23ad1c28ae345905d5293a8c5395f37d43", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.freeze_map);
    try std.testing.expectEqualStrings("aligned", manifest.freeze_boundary_status);
    try std.testing.expect(!manifest.freeze_status_change_claimed);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);
    try std.testing.expectEqual(@as(usize, 3), manifest.allowed_evidence_kinds.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.forbidden_transport_claims.len);
    try std.testing.expect(manifest.architecture_council_reopen_required);
    try std.testing.expect(!manifest.architecture_council_reopen_attached);
    try std.testing.expect(manifest.survey_summary.virtio_mmio_c_lines >= 800);
    try std.testing.expectEqual(@as(usize, 11), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_core_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_test_present);
    try std.testing.expect(manifest.gaps.len >= 17);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_STATUS=parked") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_BOUNDARY_STATUS=aligned") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_STATUS_CHANGE_CLAIMED=false") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=true") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=false") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Allowed roadmap destinations for bounded follow-on work in this blocked packet remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this survey does not claim a wider transport-facing home.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe or remove lifecycle behavior.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Any status review beyond this blocked-on-risky-transport packet still needs an Architecture Council reopen request with fresh linked evidence attached; this survey does not attach one.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "scripts/zigux/check-phase10-core-packet.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "scripts/zigux/check-phase10-ring-packet.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "scripts/zigux/check-phase10-input-packet.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_mmio.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shorter restaged config window clears stale second-word data") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "plans one bounded config-word write") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "config-write disposition summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "absolute end offset and changed-byte mask") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "without mutating config space") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "probe-preflight summary flips from ready to blocked") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "transport-identity summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "consumes that identity snapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "selected-queue readiness summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queue-ready-for-handoff posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "justified `zigux/kernel/` or `zigux/helpers/` support surfaces") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_core_reset_queue.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_driver_id.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_input_status_drain.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase10_virtio_mmio_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig build test --build-file zigux/tests/phase10_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase10-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase10") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "PHASE10_STATUS=parked") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "drivers/virtio/virtio_mmio.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "config-word write planning summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "config-write disposition summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "one explicit transport-identity summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "probe-preflight summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "selected-queue readiness summary") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_mmio_survey_gate = false;
    var saw_mmio_survey_note = false;
    var saw_mmio_register_helper = false;
    var saw_mmio_queue_size_helper = false;
    var saw_mmio_slice_note = false;
    var saw_mmio_feature_selector = false;
    var saw_mmio_config_window = false;
    var saw_mmio_config_write_plan = false;
    var saw_mmio_transport_identity = false;
    var saw_mmio_config_write_disposition = false;
    var saw_mmio_probe_preflight = false;
    var saw_mmio_selected_queue_readiness = false;
    var saw_mmio_lifecycle_blocker = false;
    var saw_ring_helper = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_risky_transport")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-ring-lab-helper")) {
            saw_ring_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-survey-gate")) {
            saw_mmio_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_mmio_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-survey-note")) {
            saw_mmio_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-mmio-survey.md", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-register-window-helper")) {
            saw_mmio_register_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register window") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-size-helper")) {
            saw_mmio_queue_size_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_num_max") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-slice-note")) {
            saw_mmio_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-mmio-slice.md", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-feature-word-selector-helper")) {
            saw_mmio_feature_selector = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "device-feature selector") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-window-helper")) {
            saw_mmio_config_window = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-word window") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shorter restaged config window") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shrinks the readable config window") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-plan-helper")) {
            saw_mmio_config_write_plan = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-word write plan") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "previous word value") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without mutating config space") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-transport-identity-helper")) {
            saw_mmio_transport_identity = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "transport-identity summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "device ID") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without widening into interrupt acknowledgement") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-disposition-helper")) {
            saw_mmio_config_write_disposition = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "absolute end of the prepared config-word window") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "changed-byte mask") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without mutating config space") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-probe-preflight-helper")) {
            saw_mmio_probe_preflight = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_mmio_probe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared identity snapshot") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without widening into lifecycle") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-selected-queue-readiness-helper")) {
            saw_mmio_selected_queue_readiness = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_num_max") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-ready-for-handoff posture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without widening into queue discovery") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {
            saw_mmio_lifecycle_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue discovery") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe or remove lifecycle") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(starter_landed_count >= 16);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_ring_helper);
    try std.testing.expect(saw_mmio_survey_gate);
    try std.testing.expect(saw_mmio_survey_note);
    try std.testing.expect(saw_mmio_register_helper);
    try std.testing.expect(saw_mmio_queue_size_helper);
    try std.testing.expect(saw_mmio_slice_note);
    try std.testing.expect(saw_mmio_feature_selector);
    try std.testing.expect(saw_mmio_config_window);
    try std.testing.expect(saw_mmio_config_write_plan);
    try std.testing.expect(saw_mmio_transport_identity);
    try std.testing.expect(saw_mmio_config_write_disposition);
    try std.testing.expect(saw_mmio_probe_preflight);
    try std.testing.expect(saw_mmio_selected_queue_readiness);
    try std.testing.expect(saw_mmio_lifecycle_blocker);
}
