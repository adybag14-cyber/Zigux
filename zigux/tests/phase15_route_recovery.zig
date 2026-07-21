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

test "phase 15 route recovery keeps wrappers and shared CI explicit" {
    const note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(note);
    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectContains(note, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
    try expectContains(note, "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true");
    try expectContains(makefile, "phase15-validate:");
    try expectContains(makefile, "phase15-test:");
    try expectContains(makefile, "phase15: phase15-validate phase15-test");
    try expectContains(workflow, "- name: Validate current Phase 15 governance packet");
    try expectContains(workflow, "run: make -C zigux phase15-validate");
    try expectContains(workflow, "- name: Run current Phase 15 governance tests");
    try expectContains(workflow, "run: make -C zigux phase15-test");
    try expectContains(workflow, "- name: Run current Phase 15 aggregate route");
    try expectContains(workflow, "run: make -C zigux phase15");
}

test "phase 15 route recovery leaves governance boundaries unchanged" {
    const note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(note);
    const readiness = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json");
    defer std.testing.allocator.free(readiness);
    const gaps = try readRepoFile("zigux/tests/phase15_readiness_gap_matrix.json");
    defer std.testing.allocator.free(gaps);

    try expectContains(note, "PHASE15_FREEZE_MAP_STATUS_CHANGE=false");
    try expectContains(note, "PHASE15_STUDY_ONLY_BOUNDARY_UNCHANGED=true");
    try expectContains(readiness, "\"phase15_validate_target_present\": true");
    try expectContains(readiness, "\"phase15_test_target_present\": true");
    try expectContains(readiness, "\"phase15_aggregate_target_present\": true");
    try expectContains(readiness, "\"shared_ci_phase15_present\": true");
    try expectContains(readiness, "\"phase15_replay_green_on_current_master\": true");
    try expectContains(readiness, "\"missing_make_targets\": []");
    try expectContains(readiness, "\"missing_workflow_phase15_route\": false");
    try expectContains(gaps, "\"remaining_readiness_gap_count\": 1");
    try expectContains(gaps, "\"gap\": \"no_architecture_council_status_change_approval\"");
    try expectContains(gaps, "\"status\": \"blocked\"");
}
