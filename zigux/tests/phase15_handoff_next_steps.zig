const std = @import("std");

const HandoffManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    handoff_note: []const u8,
    checker: []const u8,
    present_paths: []const []const u8,
    still_missing_paths: []const []const u8,
    required_markers: []const []const u8,
    checker_group_markers: []const []const u8,
    handoff_rule_markers: []const []const u8,
    roadmap_alignment_markers: []const []const u8,
    pending_next_step_markers: []const []const u8,
    next_bounded_future_target_markers: []const []const u8,
    missing_route_markers: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

test "phase 15 handoff manifest records the focused replay, readiness matrix, scripts-root checker, and shared build companion as landed packet evidence" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_handoff_next_steps_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(HandoffManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-29", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-handoff-next-steps-survey.md", manifest.handoff_note);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-handoff-note-alignment.py", manifest.checker);
    try std.testing.expectEqual(@as(usize, 43), manifest.present_paths.len);
    try std.testing.expectEqual(@as(usize, 0), manifest.still_missing_paths.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.required_markers.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.checker_group_markers.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.handoff_rule_markers.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_alignment_markers.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.pending_next_step_markers.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.next_bounded_future_target_markers.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.missing_route_markers.len);

    try expectSliceContains(manifest.present_paths, "Documentation/zigux/phase15-deep-core-blocker-survey.md");
    try expectSliceContains(manifest.present_paths, "zigux-alpha/README.md");
    try expectSliceContains(manifest.present_paths, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_freeze_map_governance.zig");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_parity_scorecard.json");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_parity_scorecard.zig");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_architecture_council_review_process.zig");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_readiness_gap_matrix.json");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_handoff_next_steps.zig");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_build.zig");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectSliceContains(manifest.present_paths, "scripts/zigux/check-phase15-docs-readme-alignment.py");
    try expectSliceContains(manifest.present_paths, "scripts/zigux/check-phase15-scripts-readme-alignment.py");
    try expectSliceContains(manifest.present_paths, "scripts/zigux/check-phase15-architecture-council-packet.py");
    try expectSliceContains(manifest.present_paths, "scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectSliceContains(manifest.present_paths, "scripts/zigux/validate-phase15.py");
    try expectSliceContains(manifest.required_markers, "The readiness gap matrix `zigux/tests/phase15_readiness_gap_matrix.json` is directly materialized on current `master` and keeps the roadmap-versus-ledger release blockers explicit as data rather than prose-only handoff notes.");
    try expectSliceContains(manifest.next_bounded_future_target_markers, "reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift");
    try expectSliceContains(manifest.next_bounded_future_target_markers, "reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default");
    try expectSliceContains(manifest.next_bounded_future_target_markers, "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet");
    try expectSliceContains(manifest.missing_route_markers, "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectSliceContains(manifest.missing_route_markers, "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`");
}

test "phase 15 handoff note treats the focused replay, readiness matrix, scripts-root checker, and shared build companion as present while wrapper and shared-CI routes stay blocked" {
    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 64 * 1024);
    defer std.testing.allocator.free(handoff_note);

    const manifest_json = try readRepoFile("zigux/tests/phase15_handoff_next_steps_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(HandoffManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try expectContains(handoff_note, "PHASE15_STATUS=handoff_next_steps_survey_landed");
    try expectContains(handoff_note, "PHASE15_LANE_KEY=P15-L12");
    try expectContains(handoff_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(handoff_note, manifest.surveyed_commit);
    try expectContains(handoff_note, "The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`");
    try expectContains(handoff_note, "The readiness gap matrix `zigux/tests/phase15_readiness_gap_matrix.json` is directly materialized on current `master` and keeps the roadmap-versus-ledger release blockers explicit as data rather than prose-only handoff notes.");
    try expectContains(handoff_note, "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_readiness_gap_matrix.json`, `zigux/tests/phase15_build.zig`, and `scripts/zigux/check-phase15-blocked-route-recovery.py` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.");
    try expectContains(handoff_note, "The dedicated validator `scripts/zigux/validate-phase15.py`, the dedicated Architecture Council packet checker `scripts/zigux/check-phase15-architecture-council-packet.py`, the readiness gap matrix `zigux/tests/phase15_readiness_gap_matrix.json`, the shared build companion `zigux/tests/phase15_build.zig`, and the blocked-route recovery checker `scripts/zigux/check-phase15-blocked-route-recovery.py` are directly materialized on current `master`, but they do not by themselves land the broader dedicated `phase15*` wrapper routes or shared-CI route.");
    try expectNotContains(handoff_note, "no dedicated handoff-specific Zig replay is directly materialized on current `master`");

    for (manifest.present_paths) |path| {
        try expectContains(handoff_note, path);
    }
    for (manifest.still_missing_paths) |path| {
        try expectContains(handoff_note, path);
    }
    for (manifest.required_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.checker_group_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.handoff_rule_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.roadmap_alignment_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.pending_next_step_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.next_bounded_future_target_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.missing_route_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
}
