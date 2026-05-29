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

test "Lane 01 roadmap keeps licensing from becoming an expansion shortcut" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "## Licensing and Reuse Policy");
    try expectContains(roadmap, "For Zigux product work, licensing is not the blocker.");
    try expectContains(roadmap, "Legal permission expands the implementation options.");
    try expectContains(roadmap, "It does not justify mirror-tree sprawl, unclear ownership, or skipping validation.");
}

test "Lane 01 roadmap ties reuse permission to reviewable sources" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "Working rule for this repo:");
    try expectContains(roadmap, "direct copies from same-license Zigux or ZAR material are allowed when legally valid and reviewable");
    try expectContains(roadmap, "machine translations or human translations from Linux C into Zig are allowed when legally valid and reviewable");
    try expectContains(roadmap, "adaptations from Linux, ZAR, or other same-license material are allowed when legally valid and reviewable");
}

test "Lane 01 roadmap requires engineering discipline after legal permission" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "That does not remove engineering discipline.");
    try expectContains(roadmap, "Even when copying or translating is legally allowed, the product still requires:");
    try expectContains(roadmap, "- bounded scope");
    try expectContains(roadmap, "- explicit ownership");
    try expectContains(roadmap, "- parity and validation gates");
    try expectContains(roadmap, "- rollback paths");
    try expectContains(roadmap, "- maintainable placement in the Linux-owned tree");
}

test "Lane 01 licensing packet stays before non-negotiable product rules" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectBefore(roadmap, "## Licensing and Reuse Policy", "## Non-Negotiable Product Rules");
    try expectBefore(roadmap, "It does not justify mirror-tree sprawl, unclear ownership, or skipping validation.", "## Non-Negotiable Product Rules");
}
