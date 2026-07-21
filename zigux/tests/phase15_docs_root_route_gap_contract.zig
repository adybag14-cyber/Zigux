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

test "Phase 15 wrapper and shared-CI routes are shipped" {
    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    try expectContains(makefile, "phase15-validate:");
    try expectContains(makefile, "phase15-test:");
    try expectContains(makefile, "phase15: phase15-validate phase15-test");
    try expectContains(workflow, "Validate current Phase 15 governance packet");
    try expectContains(workflow, "Run current Phase 15 governance tests");
    try expectContains(workflow, "Run current Phase 15 aggregate route");
}

test "historical route-gap prose is explicitly superseded" {
    const docs = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs);
    try expectContains(docs, "historical survey findings superseded by this current-state block");
    try expectContains(docs, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
}
