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

test "scripts README exposes current Phase 15 maintenance routes" {
    const readme = try readRepoFile("scripts/zigux/README.md");
    defer std.testing.allocator.free(readme);
    for ([_][]const u8{
        "PHASE15_ROUTE_RECOVERY_STATUS=landed",
        "make -C zigux phase15-validate",
        "make -C zigux phase15-test",
        "make -C zigux phase15",
        "Documentation/zigux/phase15-route-recovery.md",
    }) |marker| try expectContains(readme, marker);
}

test "scripts alignment checker uses the route-recovery source of truth" {
    const checker = try readRepoFile("scripts/zigux/check_phase15_scripts_readme_alignment.zig");
    defer std.testing.allocator.free(checker);
    try expectContains(checker, "Documentation/zigux/phase15-route-recovery.md");
    try expectContains(checker, "No Architecture Council approval is recorded by route recovery");
}
