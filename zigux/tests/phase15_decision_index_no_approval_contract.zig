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

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 15 decision index keeps approval inventory at zero" {
    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md");
    defer std.testing.allocator.free(decision_index);
    const readiness = try readRepoFile("zigux/tests/phase15_readiness_gap_matrix.json");
    defer std.testing.allocator.free(readiness);

    try expectContains(decision_index, "Architecture Council");
    try expectContains(readiness, "\"gap\": \"no_architecture_council_status_change_approval\"");
    try expectContains(readiness, "\"status\": \"blocked\"");
}

test "route recovery never becomes approval evidence" {
    const route_note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(route_note);
    try expectContains(route_note, "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true");
    try expectContains(route_note, "PHASE15_FREEZE_MAP_STATUS_CHANGE=false");
    try expectNotContains(route_note, "Architecture Council approval is recorded by route recovery");
}
