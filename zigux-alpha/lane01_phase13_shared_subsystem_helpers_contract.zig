const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn sectionBetween(start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, roadmap, start_marker) orelse return error.MissingStartMarker;
    const after_start = roadmap[start_index..];
    const relative_end = std.mem.indexOf(u8, after_start, end_marker) orelse return error.MissingEndMarker;
    return after_start[0..relative_end];
}

test "phase13 shared subsystem helper goal stays bounded to helper layers" {
    const phase13 = try sectionBetween(
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );

    try requireContains(phase13, "Primary product goal:");
    try requireContains(phase13, "- port bounded helper layers shared across multiple runtime consumers");
    try requireNotContains(phase13, "high-value, high-risk drivers");
    try requireNotContains(phase13, "study or wrap critical shared infrastructure");
}

test "phase13 keeps exact shared helper anchor roster visible" {
    const phase13 = try sectionBetween(
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );

    try requireContains(phase13, "Primary Linux anchors:");
    try requireContains(phase13, "- `fs/libfs.c`");
    try requireContains(phase13, "- `lib/devres.c`");
    try requireContains(phase13, "- `security/landlock/ruleset.c`");
    try requireContains(phase13, "- `security/landlock/syscalls.c`");
}

test "phase13 preserves lifetime filesystem and security helper feature boundaries" {
    const phase13 = try sectionBetween(
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );

    try requireContains(phase13, "Required Zigux features:");
    try requireContains(phase13, "- filesystem helper wrappers");
    try requireContains(phase13, "- resource lifetime helpers");
    try requireContains(phase13, "- bounded security helper pilots");
    try requireNotContains(phase13, "- boundary maps");
    try requireNotContains(phase13, "- concurrency audits");
}

test "phase13 destinations and neighboring order stay explicit" {
    const phase13 = try sectionBetween(
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );

    try requireContains(phase13, "Recommended Zigux destinations:");
    try requireContains(phase13, "- `fs/libfs.zig`");
    try requireContains(phase13, "- `lib/devres.zig`");
    try requireContains(phase13, "- `security/landlock/*.zig`");

    try requireOrdered("## Phase 12: Complex Production Drivers and Heavy Helper Consumers", "## Phase 13: Shared Subsystem Helpers");
    try requireOrdered("## Phase 13: Shared Subsystem Helpers", "## Phase 14: Core-Adjacent Bounded Internals");
}
