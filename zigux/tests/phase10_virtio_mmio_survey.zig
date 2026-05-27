const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio mmio survey note keeps the direct lab gate, packet-local companions, manifest companion, dedicated survey gate explicit beside the helper-local packet" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
    );
    defer allocator.free(survey_note);

    const build_file = try readRepoRelative(allocator, "zigux/tests/phase10_build.zig");
    defer allocator.free(build_file);

    const apply_observation_replay = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    );
    defer allocator.free(apply_observation_replay);

    try expectContains(survey_note, "PHASE10_STATUS=parked");
    try expectContains(survey_note, "lane key: `P10-L11`");
    try expectContains(survey_note, "drivers/virtio/virtio_mmio.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_mmio_verify.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_mmio.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_mmio_manifest.json");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig");
    try expectContains(survey_note, "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig");
    try expectContains(survey_note, "Documentation/zigux/phase10-virtio-mmio-slice.md");
    try expectContains(survey_note, "probe preflight gating");
    try expectContains(survey_note, "selected-queue readiness");
    try expectContains(survey_note, "interrupt-ack disposition review");
    try expectContains(survey_note, "staged config-write planning");
    try expectContains(survey_note, "config-write apply observation");
    try expectContains(survey_note, "config-write disposition reporting");
    try expectContains(survey_note, "feature-negotiation deltas");
    try expectContains(survey_note, "dedicated MMIO lab replay");
    try expectContains(survey_note, "zig test zigux/tests/phase10_virtio_mmio.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_mmio_survey.zig");
    try expectContains(
        survey_note,
        "zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all",
    );
    try expectContains(survey_note, "zig test zigux/tests/phase10_virtio_mmio_survey.zig");
    try expectContains(
        survey_note,
        "checker-backed packet-local or shared reminder surface repair",
    );
    try expectContains(build_file, "\"phase10-virtio-mmio-tests\"");
    try expectContains(build_file, "phase10_virtio_mmio_survey_module");
    try expectContains(build_file, "\"phase10-virtio-mmio-survey-tests\"");
    try expectContains(build_file, "run_phase10_virtio_mmio_tests.step");
    try expectContains(build_file, "run_phase10_virtio_mmio_survey_tests.step");
    try expectContains(
        apply_observation_replay,
        "test \"phase10 virtio mmio apply-observation replay clears stale plans across config restaging\" {",
    );
    try expectContains(
        apply_observation_replay,
        "apply_observation.summarizeConfigWriteApplyObservation(&device),",
    );
    try expectContains(
        apply_observation_replay,
        "try std.testing.expectEqual(@as(u4, 0b0001), refreshed.changed_byte_mask);",
    );
    try expectContains(
        apply_observation_replay,
        "try std.testing.expectEqual(@as(u3, 1), apply_observation.changedByteCount(refreshed));",
    );

    const replay_build_file = try readRepoRelative(
        allocator,
        "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
    );
    defer allocator.free(replay_build_file);
    try expectContains(replay_build_file, "phase10_virtio_mmio_apply_observation_replay.zig");
    try expectContains(replay_build_file, "\"phase10-virtio-mmio-apply-observation-replay\"");
    try expectContains(
        replay_build_file,
        "Run the bounded Phase 10 virtio MMIO apply-observation replay",
    );
}

test "phase10 virtio mmio survey packet keeps the config-write companion and slice note explicit" {
    const allocator = std.testing.allocator;

    const companion_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    );
    defer allocator.free(companion_note);

    const slice_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-mmio-slice.md",
    );
    defer allocator.free(slice_note);

    try expectContains(
        companion_note,
        "# Phase 10 virtio MMIO Config-Write Disposition Companion",
    );
    try expectContains(
        companion_note,
        "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion",
    );
    try expectContains(
        companion_note,
        "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion",
    );
    try expectContains(
        companion_note,
        "`previous_value` and `planned_value` so a reviewer can compare the staged write against the existing config bytes",
    );
    try expectContains(
        companion_note,
        "`changed_byte_mask` so byte-level deltas are visible without replaying the full word manually",
    );
    try expectContains(
        companion_note,
        "`has_changes` derived from the actual byte-delta mask rather than a blanket true result",
    );
    try expectContains(
        companion_note,
        "`error.ConfigWritePlanUnavailable` when no current staged plan is available",
    );
    try expectContains(slice_note, "# Phase 10 Virtio MMIO Slice");
    try expectContains(slice_note, "scripts/zigux/check-phase10-mmio-packet.py");
    try expectContains(slice_note, "planning-only config-write observation");
    try expectContains(
        slice_note,
        "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice",
    );
}

test "phase10 virtio mmio survey packet keeps the shared review companion aligned with the MMIO packet" {
    const allocator = std.testing.allocator;

    const review_companion = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    );
    defer allocator.free(review_companion);

    try expectContains(review_companion, "helper-local MMIO packet anchors:");
    try expectContains(review_companion, "`Documentation/zigux/phase10-virtio-mmio-survey.md`");
    try expectContains(review_companion, "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`");
    try expectContains(review_companion, "`Documentation/zigux/phase10-virtio-mmio-slice.md`");
    try expectContains(review_companion, "`drivers/virtio/virtio_mmio.zig`");
    try expectContains(review_companion, "`drivers/virtio/virtio_mmio_verify.zig`");
    try expectContains(review_companion, "`zigux/tests/phase10_virtio_mmio_manifest.json`");
    try expectContains(review_companion, "`zigux/tests/phase10_virtio_mmio.zig`");
    try expectContains(review_companion, "`zigux/tests/phase10_virtio_mmio_survey.zig`");
    try expectContains(review_companion, "`scripts/zigux/check-phase10-mmio-packet.py`");
    try expectContains(review_companion, "`zigux/tests/phase10_build.zig`");
}

test "phase10 virtio mmio survey gate keeps survey-note lane identity, lane sequencing ownership, helper inventory, and risky transport posture explicit" {
    const allocator = std.testing.allocator;

    const lane_sequencing_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    );
    defer allocator.free(lane_sequencing_note);

    const manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_mmio_manifest.json",
    );
    defer allocator.free(manifest);

    try expectContains(
        lane_sequencing_note,
        "MMIO lane `P10-L11` owns the bounded MMIO helper packet",
    );
    try expectContains(manifest, "\"lane_key\": \"P10-L11\"");
    try expectContains(manifest, "\"risky_transport_posture\": \"blocked_on_risky_transport\"");
    try expectContains(manifest, "\"id\": \"phase10-mmio-interrupt-ack-disposition-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-mmio-feature-negotiation-summary-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-mmio-config-write-plan-freshness-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-mmio-config-write-apply-observation-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-mmio-survey-gate\"");
}

test "phase10 virtio mmio survey gate keeps helper-local queue isolation and probe blockers explicit" {
    const allocator = std.testing.allocator;

    const helper_tests = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_mmio.zig",
    );
    defer allocator.free(helper_tests);

    try expectContains(
        helper_tests,
        "test \"phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes\" {",
    );
    try expectContains(
        helper_tests,
        "test \"phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit\" {",
    );
    try expectContains(
        helper_tests,
        "test \"phase10 virtio mmio keeps config-write planning bounded to staged review state\" {",
    );
    try expectContains(
        helper_tests,
        "test \"phase10 virtio mmio keeps stale config-write plans unavailable after generation drift\" {",
    );
    try expectContains(
        helper_tests,
        "test \"phase10 virtio mmio keeps config-write disposition planning-only across restaging\" {",
    );
    try expectContains(
        helper_tests,
        "test \"phase10 virtio mmio apply observation keeps touched and changed bytes reviewable without mutating config bytes\" {",
    );
    try expectContains(
        helper_tests,
        "try std.testing.expect(!summary.bounded_queue_register_window_ready);",
    );
    try expectContains(
        helper_tests,
        "try std.testing.expect(!summary.interrupt_ack_ready);",
    );
    try expectContains(
        helper_tests,
        "try std.testing.expect(summary.queue_ready_for_handoff);",
    );
}

test "phase10 virtio mmio survey note keeps risky transport work and freeze-boundary policy evidence explicit" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
    );
    defer allocator.free(survey_note);

    try expectContains(survey_note, "transport-backed queue setup or queue reset execution");
    try expectContains(survey_note, "shared IRQ delivery parity");
    try expectContains(survey_note, "DMA-facing behavior");
    try expectContains(
        survey_note,
        "probe, remove, freeze, restore, or device-lifecycle closure",
    );
    try expectContains(
        survey_note,
        "`freeze_boundary_status` stays `aligned` and `freeze_status_change_claimed` stays `false`.",
    );
    try expectContains(
        survey_note,
        "`architecture_council_reopen_required` stays `true` and `architecture_council_reopen_attached` stays `false`.",
    );
    try expectContains(
        survey_note,
        "allowed evidence kinds stay limited to `driver_local_lab_slices`, `survey_manifests`, and `shared_validation_gates`.",
    );
    try expectContains(
        survey_note,
        "allowed roadmap destinations stay limited to `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`.",
    );
    try expectContains(
        survey_note,
        "forbidden transport claims remain `queue_setup_reset_paths`, `queue_reset_execution`, `irq_parity`, `dma_paths`, `probe_remove_lifecycle`, and `freeze_restore_lifecycle`.",
    );
}
