const std = @import("std");

const SequencingManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    sequencing_note: []const u8,
    readiness_manifest: []const u8,
    shared_summary_gap_note: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    maintenance_replay_commands: []const []const u8,
};

const RepoEvidence = struct {
    phase15_readiness_packet_checker_present: bool,
    phase15_validator_script_present: bool,
    phase15_docs_readme_checker_present: bool,
    phase15_tests_readme_checker_present: bool,
    phase15_governance_lane_manifest_present: bool,
    phase15_governance_lane_replay_present: bool,
    phase15_handoff_manifest_present: bool,
    phase15_build_zig_present: bool,
    phase15_indefinite_c_lane_owner_alignment_present: bool,
    phase15_makefile_present: bool,
    phase15_validate_target_present: bool,
    phase15_test_target_present: bool,
    phase15_aggregate_target_present: bool,
    shared_ci_phase15_present: bool,
    phase15_replay_green_on_current_master: bool,
};

const ReadinessManifest = struct {
    surveyed_commit_mode: []const u8,
    surveyed_commit: []const u8,
    readiness_packet_checker: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    repo_evidence: RepoEvidence,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn expectSliceNotContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return error.TestUnexpectedResult;
    }
}

test "phase 15 governance-lane sequencing manifest records the current direct packet" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_governance_lane_sequencing_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(SequencingManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("arch-council", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-22", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-governance-lane-sequencing.md", manifest.sequencing_note);
    try std.testing.expectEqualStrings("zigux/tests/phase15_readiness_gate_manifest.json", manifest.readiness_manifest);
    try std.testing.expectEqual(@as(usize, 19), manifest.direct_packet_paths.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.still_missing_broader_paths.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.maintenance_replay_commands.len);

    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_parity_scorecard.json");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_parity_scorecard.zig");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectSliceContains(manifest.direct_packet_paths, "scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectSliceContains(manifest.still_missing_broader_paths, "scripts/zigux/validate-phase15.py");
    try expectSliceContains(manifest.still_missing_broader_paths, "zigux/tests/phase15_build.zig");
    try expectSliceNotContains(manifest.still_missing_broader_paths, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectSliceContains(manifest.maintenance_replay_commands, "python3 scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectSliceContains(manifest.maintenance_replay_commands, "zig test zigux/tests/phase15_governance_lane_sequencing.zig");
}

test "phase 15 governance-lane sequencing note names the current packet and current gaps honestly" {
    const sequencing_note = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 24 * 1024);
    defer std.testing.allocator.free(sequencing_note);

    const manifest_json = try readRepoFile("zigux/tests/phase15_governance_lane_sequencing_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(SequencingManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try expectContains(sequencing_note, "PHASE15_STATUS=governance_lane_sequencing_packet_landed");
    try expectContains(sequencing_note, "PHASE15_LANE_KEY=arch-council");
    try expectContains(sequencing_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(sequencing_note, manifest.surveyed_commit);
    try expectContains(sequencing_note, "the focused parity-scorecard machine-readable companion plus focused replay are landed");
    try expectContains(sequencing_note, "`zigux/tests/phase15_parity_scorecard.json`");
    try expectContains(sequencing_note, "`zigux/tests/phase15_parity_scorecard.zig`");
    try expectContains(sequencing_note, "the dedicated handoff manifest plus focused handoff-specific replay plus focused handoff-note checker are landed");
    try expectContains(sequencing_note, "`zigux/tests/phase15_handoff_next_steps_manifest.json`");
    try expectContains(sequencing_note, "`scripts/zigux/check-phase15-handoff-note-alignment.py`");
    try expectContains(sequencing_note, "python3 scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectContains(sequencing_note, "zig test zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectContains(sequencing_note, "a missing focused replay, dedicated build file, or other absent broader companion is already landed on current `master`");
    try expectContains(sequencing_note, "broader validator-first and dedicated-build companions");
    try expectContains(sequencing_note, "which remaining missing validator-first or dedicated-build companions");

    for (manifest.still_missing_broader_paths) |path| {
        try expectContains(sequencing_note, path);
    }
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig") == null);
}

test "phase 15 readiness manifest records the lane-owner replay as direct packet evidence" {
    const readiness_json = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(readiness_json);

    const parsed = try std.json.parseFromSlice(ReadinessManifest, std.testing.allocator, readiness_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const readiness = parsed.value;

    try std.testing.expectEqualStrings("dated_master_readback", readiness.surveyed_commit_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-22", readiness.surveyed_commit);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-readiness-gate-packet.py", readiness.readiness_packet_checker);
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_parity_scorecard.json");
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_parity_scorecard.zig");
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectSliceNotContains(readiness.still_missing_broader_paths, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try std.testing.expect(readiness.repo_evidence.phase15_indefinite_c_lane_owner_alignment_present);
}
