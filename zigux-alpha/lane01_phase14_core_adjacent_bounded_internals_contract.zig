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

test "phase 14 keeps core-adjacent work study or wrapper first" {
    const phase14 = try sectionBetween(
        roadmap,
        "## Phase 14: Core-Adjacent Bounded Internals",
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    );

    try expectContains(phase14, "Primary product goal:\n- study or wrap critical shared infrastructure without claiming premature parity");
    try expectContains(phase14, "Required Zigux features:");
    try expectContains(phase14, "- boundary maps");
    try expectContains(phase14, "- concurrency audits");
    try expectContains(phase14, "- explicit stay-in-C decisions where warranted");
    try expectContains(phase14, "- wrapper-first or study-only posture");
}

test "phase 14 keeps exact core-adjacent anchor roster visible" {
    const phase14 = try sectionBetween(
        roadmap,
        "## Phase 14: Core-Adjacent Bounded Internals",
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    );

    try expectContains(phase14, "Primary Linux anchors:");
    try expectContains(phase14, "- `kernel/workqueue.c`");
    try expectContains(phase14, "- `kernel/trace/ring_buffer.c`");
    try expectContains(phase14, "- `net/core/skbuff.c`");
    try expectContains(phase14, "- `kernel/rcu/tree.c`");
}

test "phase 14 keeps bridge destinations bounded and ring buffer caveated" {
    const phase14 = try sectionBetween(
        roadmap,
        "## Phase 14: Core-Adjacent Bounded Internals",
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    );

    try expectContains(phase14, "Recommended Zigux destinations:");
    try expectContains(phase14, "- `kernel/workqueue_bridge.zig`");
    try expectContains(phase14, "- `kernel/trace/ring_buffer.zig` only if years of evidence justify it");
    try expectContains(phase14, "- `net/core/skbuff_bridge.zig`");
    try expectContains(phase14, "- `kernel/rcu/tree_bridge.zig`");
    try std.testing.expect(std.mem.indexOf(u8, phase14, "zigux-alpha/") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase14, "drivers/") == null);
}

test "phase 14 stays after shared subsystem helpers and before governance blockers" {
    try expectBefore(
        roadmap,
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );
    try expectBefore(
        roadmap,
        "## Phase 14: Core-Adjacent Bounded Internals",
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    );
}
