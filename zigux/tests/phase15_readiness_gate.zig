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

const RepoEvidence = struct {
    phase15_validate_target_present: bool,
    phase15_test_target_present: bool,
    phase15_aggregate_target_present: bool,
    shared_ci_phase15_present: bool,
    phase15_replay_green_on_current_master: bool,
};
const BlockedBroaderRoutes = struct {
    missing_make_targets: []const []const u8,
    missing_workflow_phase15_route: bool,
};
const Manifest = struct {
    surveyed_commit_mode: []const u8,
    surveyed_commit: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    blocked_broader_routes: BlockedBroaderRoutes,
    repo_evidence: RepoEvidence,
    phase15_validate_checkers: []const []const u8,
};

test "phase 15 readiness manifest records recovered wrapper and CI routes" {
    const source = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json");
    defer std.testing.allocator.free(source);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("current_master_replay", manifest.surveyed_commit_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-07-21", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 0), manifest.still_missing_broader_paths.len);
    try std.testing.expectEqual(@as(usize, 0), manifest.blocked_broader_routes.missing_make_targets.len);
    try std.testing.expect(!manifest.blocked_broader_routes.missing_workflow_phase15_route);
    try std.testing.expect(manifest.repo_evidence.phase15_validate_target_present);
    try std.testing.expect(manifest.repo_evidence.phase15_test_target_present);
    try std.testing.expect(manifest.repo_evidence.phase15_aggregate_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.phase15_replay_green_on_current_master);
    try expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-route-recovery.md");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_route_recovery.zig");
    try expectSliceContains(manifest.phase15_validate_checkers, "scripts\\zigux/check_phase15_blocked_route_recovery.zig");
}

test "phase 15 gap matrix leaves only the approval blocker" {
    const gaps = try readRepoFile("zigux/tests/phase15_readiness_gap_matrix.json");
    defer std.testing.allocator.free(gaps);
    try expectContains(gaps, "\"remaining_readiness_gap_count\": 1");
    try expectContains(gaps, "\"blocked_make_route_count\": 0");
    try expectContains(gaps, "\"blocked_workflow_route_count\": 0");
    try expectContains(gaps, "\"release_evidence_count\": 7");
    try expectContains(gaps, "\"gap\": \"no_architecture_council_status_change_approval\"");
    try expectContains(gaps, "\"status\": \"blocked\"");
}

test "phase 15 readiness note points to the current route contract" {
    const note = try readRepoFile("Documentation/zigux/phase15-readiness-gate-survey.md");
    defer std.testing.allocator.free(note);
    try expectContains(note, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
    try expectContains(note, "Documentation/zigux/phase15-route-recovery.md");
    try expectContains(note, "zigux/tests/phase15_route_recovery.zig");
    try expectContains(note, "No Architecture Council approval is recorded by route recovery");
}
