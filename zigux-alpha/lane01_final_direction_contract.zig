const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, roadmap, needle) != null);
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "final direction keeps disciplined product-program closeout" {
    try expectContains("## Final Direction");
    try expectContains("Zigux succeeds if it behaves like a disciplined Linux product program, not like a language rewrite experiment.");
    try expectContains("That means:");
    try expectContains("- small support root");
    try expectContains("- co-located subsystem ports");
    try expectContains("- strong validation");
    try expectContains("- explicit freeze map");
    try expectContains("- commit trains that move from bounded helper wins to toolchain maturity to substrate maturity to runtime pilots");
}

test "final direction preserves ZAR investment test" {
    try expectContains("ZAR future work should now be judged against one question:");
    try expectContains("- does this make a future Zigux commit smaller, safer, or more testable?");
    try expectContains("If yes, keep investing.");
    try expectContains("If no, keep it in research and do not let it drive the product roadmap.");
}

test "final direction stays after immediate next steps and closes the roadmap" {
    try expectOrder("## What Should Start Next in Zigux", "## Final Direction");

    const final_index = std.mem.indexOf(u8, roadmap, "## Final Direction") orelse return error.MissingFinalDirection;
    const next_heading = std.mem.indexOfPos(u8, roadmap, final_index + "## Final Direction".len, "\n## ");
    try std.testing.expect(next_heading == null);
}
