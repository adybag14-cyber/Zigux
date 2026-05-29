const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "Lane 01 roadmap keeps Phase 5 sample work as the near-term handoff" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "### Phase 5 commits");
    try expectContains(roadmap, "17. `feat(samples/zigux): add reference samples for fifo, kobject, kretprobe, and trace events`");
    try expectContains(roadmap, "18. `docs(Documentation/zigux): add sample-backed review guide`");
    try expectBefore(roadmap, "### Phase 3 and 4 commits", "### Phase 5 commits");
    try expectBefore(roadmap, "### Phase 5 commits", "## Recommended Validation Gates");
}

test "Lane 01 roadmap blocks premature Phase 10 scheduling" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "Do not schedule Phase 10+ commits until the earlier gates are actually green.");
    try expectBefore(roadmap, "18. `docs(Documentation/zigux): add sample-backed review guide`", "Do not schedule Phase 10+ commits until the earlier gates are actually green.");
    try expectBefore(roadmap, "Do not schedule Phase 10+ commits until the earlier gates are actually green.", "## Recommended Validation Gates");
}

test "Lane 01 roadmap keeps validation gates after the scheduling boundary" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "## Recommended Validation Gates");
    try expectContains(roadmap, "1. Build gate");
    try expectContains(roadmap, "2. ABI gate");
    try expectContains(roadmap, "3. Behavior gate");
    try expectContains(roadmap, "4. Performance gate");
    try expectContains(roadmap, "5. Runtime gate");
    try expectContains(roadmap, "6. Rollback gate");
    try expectBefore(roadmap, "Do not schedule Phase 10+ commits until the earlier gates are actually green.", "## Recommended Validation Gates");
    try expectBefore(roadmap, "## Recommended Validation Gates", "## What Should Start Next in Zigux");
}
