const std = @import("std");
const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn phase14Section() []const u8 {
    const start = std.mem.indexOf(u8, roadmap, "## Phase 14: Core-Adjacent Bounded Internals") orelse unreachable;
    const end = std.mem.indexOf(u8, roadmap[start..], "## Phase 15: Full-Parity Blockers and Long-Term Governance") orelse unreachable;
    return roadmap[start .. start + end];
}

test "phase14 packet preserves study-or-wrap goal" {
    const section = phase14Section();

    try requireContains(section, "Primary product goal:\n- study or wrap critical shared infrastructure without claiming premature parity");
    try requireContains(section, "Required Zigux features:");
    try requireContains(section, "- boundary maps");
    try requireContains(section, "- concurrency audits");
    try requireContains(section, "- explicit stay-in-C decisions where warranted");
    try requireContains(section, "- wrapper-first or study-only posture");
}

test "phase14 packet preserves core-adjacent anchor roster" {
    const section = phase14Section();

    try requireContains(section, "Primary Linux anchors:");
    try requireContains(section, "- `kernel/workqueue.c`");
    try requireContains(section, "- `kernel/trace/ring_buffer.c`");
    try requireContains(section, "- `net/core/skbuff.c`");
    try requireContains(section, "- `kernel/rcu/tree.c`");
}

test "phase14 packet preserves bounded destination posture" {
    const section = phase14Section();

    try requireContains(section, "Recommended Zigux destinations:");
    try requireContains(section, "- `kernel/workqueue_bridge.zig`");
    try requireContains(section, "- `kernel/trace/ring_buffer.zig` only if years of evidence justify it");
    try requireContains(section, "- `net/core/skbuff_bridge.zig`");
    try requireContains(section, "- `kernel/rcu/tree_bridge.zig`");
}

test "phase14 remains ordered after phase13 and before phase15" {
    try requireBefore(
        roadmap,
        "## Phase 13: Shared Subsystem Helpers",
        "## Phase 14: Core-Adjacent Bounded Internals",
    );
    try requireBefore(
        roadmap,
        "## Phase 14: Core-Adjacent Bounded Internals",
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    );
}
