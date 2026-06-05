const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;

    try std.testing.expect(first_index < second_index);
}

fn sectionBetween(
    haystack: []const u8,
    start_marker: []const u8,
    end_marker: []const u8,
) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const after_start = start + start_marker.len;
    const end_relative = std.mem.indexOf(u8, haystack[after_start..], end_marker) orelse return error.MissingEndMarker;

    return haystack[after_start .. after_start + end_relative];
}

test "phase 13 keeps shared subsystem helper scope bounded" {
    const phase13 = try sectionBetween(
        roadmap,
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );

    try expectContains(phase13, "Primary product goal:\n- port bounded helper layers shared across multiple runtime consumers");
    try expectContains(phase13, "Required Zigux features:\n- filesystem helper wrappers\n- resource lifetime helpers\n- bounded security helper pilots");
}

test "phase 13 keeps exact Linux anchor roster visible" {
    const phase13 = try sectionBetween(
        roadmap,
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );

    try expectContains(phase13, "Primary Linux anchors:");
    try expectContains(phase13, "- `fs/libfs.c`");
    try expectContains(phase13, "- `lib/devres.c`");
    try expectContains(phase13, "- `security/landlock/ruleset.c`");
    try expectContains(phase13, "- `security/landlock/syscalls.c`");
}

test "phase 13 keeps destination list co-located instead of mirror-tree shaped" {
    const phase13 = try sectionBetween(
        roadmap,
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );

    try expectContains(phase13, "Recommended Zigux destinations:");
    try expectContains(phase13, "- `fs/libfs.zig`");
    try expectContains(phase13, "- `lib/devres.zig`");
    try expectContains(phase13, "- `security/landlock/*.zig`");
    try std.testing.expect(std.mem.indexOf(u8, phase13, "zigux-alpha/") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase13, "zigux/kernel/") == null);
}

test "phase 13 stays after complex drivers and before core-adjacent study" {
    try expectBefore(
        roadmap,
        "## Phase 12: Complex Production Drivers and Heavy Helper Consumers",
        "## Phase 13: Shared Subsystem Helpers",
    );
    try expectBefore(
        roadmap,
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );
}
