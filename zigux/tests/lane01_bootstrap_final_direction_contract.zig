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

test "Lane 01 roadmap final direction keeps product discipline explicit" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "## Final Direction");
    try expectContains(roadmap, "Zigux succeeds if it behaves like a disciplined Linux product program, not like a language rewrite experiment.");
    try expectContains(roadmap, "That means:");
    try expectContains(roadmap, "- small support root");
    try expectContains(roadmap, "- co-located subsystem ports");
    try expectContains(roadmap, "- strong validation");
    try expectContains(roadmap, "- explicit freeze map");
    try expectContains(roadmap, "- commit trains that move from bounded helper wins to toolchain maturity to substrate maturity to runtime pilots");
}

test "Lane 01 roadmap final direction keeps ZAR investment bounded" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "ZAR future work should now be judged against one question:");
    try expectContains(roadmap, "- does this make a future Zigux commit smaller, safer, or more testable?");
    try expectContains(roadmap, "If yes, keep investing.");
    try expectContains(roadmap, "If no, keep it in research and do not let it drive the product roadmap.");
}

test "Lane 01 final direction stays after immediate next steps" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectBefore(roadmap, "## What Should Start Next in Zigux", "## Final Direction");
    try expectBefore(roadmap, "5. do not start runtime kernel ports before the Phase 2-4 gates are in place", "## Final Direction");
    try expectBefore(roadmap, "## Final Direction", "If no, keep it in research and do not let it drive the product roadmap.");
}
