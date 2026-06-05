const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase12_heading = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers";
const phase13_heading = "## Phase 13: Shared Subsystem Helpers";
const phase14_heading = "## Phase 14: Core-Adjacent Bounded Internals";

fn sectionBetween(start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, roadmap, start) orelse return error.MissingSectionStart;
    const after_start = start_index + start.len;
    const end_index = std.mem.indexOfPos(u8, roadmap, after_start, end) orelse return error.MissingSectionEnd;
    return roadmap[after_start..end_index];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

test "phase13 packet remains between phase12 and phase14" {
    try expectBefore(roadmap, phase12_heading, phase13_heading);
    try expectBefore(roadmap, phase13_heading, phase14_heading);
}

test "phase13 shared subsystem helper scope remains bounded" {
    const phase13 = try sectionBetween(phase13_heading, phase14_heading);

    try expectContains(phase13, "Primary product goal:\n- port bounded helper layers shared across multiple runtime consumers");
    try expectContains(phase13, "Required Zigux features:");
    try expectContains(phase13, "- filesystem helper wrappers");
    try expectContains(phase13, "- resource lifetime helpers");
    try expectContains(phase13, "- bounded security helper pilots");
    try testing.expect(std.mem.indexOf(u8, phase13, "full subsystem rewrite") == null);
    try testing.expect(std.mem.indexOf(u8, phase13, "unbounded security rewrite") == null);
}

test "phase13 linux anchors stay on shared helper layers" {
    const phase13 = try sectionBetween(phase13_heading, phase14_heading);

    try expectContains(phase13, "Primary Linux anchors:");
    try expectContains(phase13, "- `fs/libfs.c`");
    try expectContains(phase13, "- `lib/devres.c`");
    try expectContains(phase13, "- `security/landlock/ruleset.c`");
    try expectContains(phase13, "- `security/landlock/syscalls.c`");
    try expectBefore(phase13, "- `fs/libfs.c`", "- `lib/devres.c`");
    try expectBefore(phase13, "- `lib/devres.c`", "- `security/landlock/ruleset.c`");
    try expectBefore(phase13, "- `security/landlock/ruleset.c`", "- `security/landlock/syscalls.c`");
}

test "phase13 destinations stay co-located with linux ownership" {
    const phase13 = try sectionBetween(phase13_heading, phase14_heading);

    try expectContains(phase13, "Recommended Zigux destinations:");
    try expectContains(phase13, "- `fs/libfs.zig`");
    try expectContains(phase13, "- `lib/devres.zig`");
    try expectContains(phase13, "- `security/landlock/*.zig`");
    try testing.expect(std.mem.indexOf(u8, phase13, "zigux-alpha/") == null);
    try testing.expect(std.mem.indexOf(u8, phase13, "zigux/helpers/landlock") == null);
}
