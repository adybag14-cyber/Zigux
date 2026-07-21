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

test "governance sequencing includes the recovered replay routes" {
    const note = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md");
    defer std.testing.allocator.free(note);
    const manifest = try readRepoFile("zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    defer std.testing.allocator.free(manifest);
    for ([_][]const u8{
        "make -C zigux phase15-validate",
        "make -C zigux phase15-test",
        "make -C zigux phase15",
    }) |command| {
        try expectContains(note, command);
        try expectContains(manifest, command);
    }
}

test "sequencing keeps route replay separate from status changes" {
    const note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(note);
    try expectContains(note, "PHASE15_FREEZE_MAP_STATUS_CHANGE=false");
    try expectContains(note, "PHASE15_STUDY_ONLY_BOUNDARY_UNCHANGED=true");
}
