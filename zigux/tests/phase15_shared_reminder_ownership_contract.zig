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

test "shared reminder roots agree on current Phase 15 ownership" {
    for ([_][]const u8{
        "Documentation/zigux/README.md",
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
    }) |path| {
        const text = try readRepoFile(path);
        defer std.testing.allocator.free(text);
        try expectContains(text, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
        try expectContains(text, "No Architecture Council approval is recorded by route recovery");
    }
}

test "shared summary keeps route recovery bounded" {
    const summary = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md");
    defer std.testing.allocator.free(summary);
    try expectContains(summary, "historical survey findings superseded by this current-state block");
    try expectContains(summary, "Documentation/zigux/phase15-route-recovery.md");
}
