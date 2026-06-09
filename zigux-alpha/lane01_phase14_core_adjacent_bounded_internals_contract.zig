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

test "phase14 core-adjacent goal stays study bounded" {
    try requireContains(roadmap, "## Phase 14: Core-Adjacent Bounded Internals");
    try requireContains(roadmap, "Primary product goal:");
    try requireContains(roadmap, "- study or wrap critical shared infrastructure without claiming premature parity");
}

test "phase14 keeps core-adjacent anchor roster explicit" {
    try requireContains(roadmap, "Primary Linux anchors:");
    try requireContains(roadmap, "- `kernel/workqueue.c`");
    try requireContains(roadmap, "- `kernel/trace/ring_buffer.c`");
    try requireContains(roadmap, "- `net/core/skbuff.c`");
    try requireContains(roadmap, "- `kernel/rcu/tree.c`");
}

test "phase14 keeps wrapper-first and stay-in-c posture explicit" {
    try requireContains(roadmap, "Required Zigux features:");
    try requireContains(roadmap, "- boundary maps");
    try requireContains(roadmap, "- concurrency audits");
    try requireContains(roadmap, "- explicit stay-in-C decisions where warranted");
    try requireContains(roadmap, "- wrapper-first or study-only posture");
}

test "phase14 destinations and neighboring order stay bounded" {
    try requireContains(roadmap, "Recommended Zigux destinations:");
    try requireContains(roadmap, "- `kernel/workqueue_bridge.zig`");
    try requireContains(roadmap, "- `kernel/trace/ring_buffer.zig` only if years of evidence justify it");
    try requireContains(roadmap, "- `net/core/skbuff_bridge.zig`");
    try requireContains(roadmap, "- `kernel/rcu/tree_bridge.zig`");

    try requireOrdered("## Phase 13: Shared Subsystem Helpers", "## Phase 14: Core-Adjacent Bounded Internals");
    try requireOrdered("## Phase 14: Core-Adjacent Bounded Internals", "## Phase 15: Full-Parity Blockers and Long-Term Governance");
}
