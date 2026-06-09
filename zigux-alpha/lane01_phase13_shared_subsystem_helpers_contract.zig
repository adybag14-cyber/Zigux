const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase13 shared subsystem helper goal stays bounded" {
    try requireContains(roadmap, "## Phase 13: Shared Subsystem Helpers");
    try requireContains(roadmap, "Primary product goal:");
    try requireContains(roadmap, "- port bounded helper layers shared across multiple runtime consumers");
}

test "phase13 keeps shared helper anchor roster explicit" {
    try requireContains(roadmap, "Primary Linux anchors:");
    try requireContains(roadmap, "- `fs/libfs.c`");
    try requireContains(roadmap, "- `lib/devres.c`");
    try requireContains(roadmap, "- `security/landlock/ruleset.c`");
    try requireContains(roadmap, "- `security/landlock/syscalls.c`");
}

test "phase13 keeps lifetime and security helper features explicit" {
    try requireContains(roadmap, "Required Zigux features:");
    try requireContains(roadmap, "- filesystem helper wrappers");
    try requireContains(roadmap, "- resource lifetime helpers");
    try requireContains(roadmap, "- bounded security helper pilots");
}

test "phase13 destinations and neighboring order stay bounded" {
    try requireContains(roadmap, "Recommended Zigux destinations:");
    try requireContains(roadmap, "- `fs/libfs.zig`");
    try requireContains(roadmap, "- `lib/devres.zig`");
    try requireContains(roadmap, "- `security/landlock/*.zig`");

    try requireOrdered("## Phase 12: Complex Production Drivers and Heavy Helper Consumers", "## Phase 13: Shared Subsystem Helpers");
    try requireOrdered("## Phase 13: Shared Subsystem Helpers", "## Phase 14: Core-Adjacent Bounded Internals");
}
