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

test "docs README points to the current Phase 15 route packet" {
    const docs = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs);
    const checker = try readRepoFile("scripts/zigux/check_phase15_docs_readme_alignment.zig");
    defer std.testing.allocator.free(checker);
    for ([_][]const u8{
        "PHASE15_ROUTE_RECOVERY_STATUS=landed",
        "Documentation/zigux/phase15-route-recovery.md",
        "make -C zigux phase15-validate",
        "make -C zigux phase15-test",
        "make -C zigux phase15",
        "No Architecture Council approval is recorded by route recovery",
    }) |marker| try expectContains(docs, marker);
    try expectContains(checker, "Documentation/zigux/phase15-route-recovery.md");
}
