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

test "docs root keeps route recovery below Architecture Council approval" {
    const docs = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs);
    const note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(note);
    try expectContains(docs, "No Architecture Council approval is recorded by route recovery");
    try expectContains(note, "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true");
    try expectContains(note, "No direct deep-core Zig delivery claim");
}

test "all freeze and study anchors remain visible" {
    const note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(note);
    for ([_][]const u8{
        "kernel/sched/core.c", "mm/page_alloc.c",            "kernel/rcu/tree.c", "net/core/skbuff.c",
        "kernel/workqueue.c",  "kernel/trace/ring_buffer.c",
    }) |anchor| try expectContains(note, anchor);
}
