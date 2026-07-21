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

test "Phase 15 readiness records landed wrapper and shared-CI evidence" {
    const readiness = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json");
    defer std.testing.allocator.free(readiness);
    const gaps = try readRepoFile("zigux/tests/phase15_readiness_gap_matrix.json");
    defer std.testing.allocator.free(gaps);

    for ([_][]const u8{
        "\"phase15_validate_target_present\": true",
        "\"phase15_test_target_present\": true",
        "\"phase15_aggregate_target_present\": true",
        "\"shared_ci_phase15_present\": true",
        "\"phase15_replay_green_on_current_master\": true",
        "\"missing_make_targets\": []",
        "\"missing_workflow_phase15_route\": false",
    }) |marker| try expectContains(readiness, marker);

    try expectContains(gaps, "\"release_evidence_count\": 7");
    try expectContains(gaps, "\"remaining_readiness_gap_count\": 1");
    try expectContains(gaps, "\"gap\": \"no_architecture_council_status_change_approval\"");
}

test "Phase 15 release evidence stays below freeze-map approval" {
    const note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(note);
    try expectContains(note, "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true");
    try expectContains(note, "PHASE15_FREEZE_MAP_STATUS_CHANGE=false");
    try expectContains(note, "PHASE15_STUDY_ONLY_BOUNDARY_UNCHANGED=true");
}
