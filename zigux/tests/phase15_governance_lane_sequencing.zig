const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| if (std.mem.eql(u8, item, needle)) return;
    return error.TestUnexpectedResult;
}

const SequencingManifest = struct {
    surveyed_commit: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    maintenance_replay_commands: []const []const u8,
};

const RepoEvidence = struct {
    phase15_validate_target_present: bool,
    phase15_test_target_present: bool,
    phase15_aggregate_target_present: bool,
    shared_ci_phase15_present: bool,
    phase15_replay_green_on_current_master: bool,
};

const ReadinessManifest = struct {
    surveyed_commit_mode: []const u8,
    surveyed_commit: []const u8,
    repo_evidence: RepoEvidence,
};

test "phase 15 governance sequencing manifest includes recovered routes" {
    const source = try readRepoFile("zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    defer std.testing.allocator.free(source);
    const parsed = try std.json.parseFromSlice(SequencingManifest, std.testing.allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("current-master-readback-2026-07-21", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 0), manifest.still_missing_broader_paths.len);
    try expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-route-recovery.md");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_route_recovery.zig");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/Makefile");
    try expectSliceContains(manifest.direct_packet_paths, ".github/workflows/zigux-bootstrap.yml");
    try expectSliceContains(manifest.maintenance_replay_commands, "make -C zigux phase15-validate");
    try expectSliceContains(manifest.maintenance_replay_commands, "make -C zigux phase15-test");
    try expectSliceContains(manifest.maintenance_replay_commands, "make -C zigux phase15");
}

test "phase 15 governance sequencing note records route recovery as replay only" {
    const note = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md");
    defer std.testing.allocator.free(note);
    try expectContains(note, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
    try expectContains(note, "historical survey findings superseded by this current-state block");
    try expectContains(note, "No Architecture Council approval is recorded by route recovery");
}

test "phase 15 readiness evidence is one-command and shared-CI replayable" {
    const source = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json");
    defer std.testing.allocator.free(source);
    const parsed = try std.json.parseFromSlice(ReadinessManifest, std.testing.allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const readiness = parsed.value;

    try std.testing.expectEqualStrings("current_master_replay", readiness.surveyed_commit_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-07-21", readiness.surveyed_commit);
    try std.testing.expect(readiness.repo_evidence.phase15_validate_target_present);
    try std.testing.expect(readiness.repo_evidence.phase15_test_target_present);
    try std.testing.expect(readiness.repo_evidence.phase15_aggregate_target_present);
    try std.testing.expect(readiness.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(readiness.repo_evidence.phase15_replay_green_on_current_master);
}
