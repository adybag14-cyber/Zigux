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

fn phase15Section() []const u8 {
    const start = std.mem.indexOf(u8, roadmap, "## Phase 15: Full-Parity Blockers and Long-Term Governance") orelse unreachable;
    const end = std.mem.indexOf(u8, roadmap[start..], "## Freeze Map for Near- and Mid-Term Planning") orelse unreachable;
    return roadmap[start .. start + end];
}

test "phase15 packet preserves governance posture" {
    const section = phase15Section();

    try requireContains(section, "Primary product goal:\n- govern the final mixed-language steady state honestly");
    try requireContains(section, "Required Zigux features:");
    try requireContains(section, "- freeze map");
    try requireContains(section, "- Architecture Council review process");
    try requireContains(section, "- parity scorecard");
    try requireContains(section, "- policy for code that remains in C indefinitely");
    try requireContains(section, "This phase is about discipline, not bravado.");
}

test "phase15 packet preserves full-parity blocker anchors" {
    const section = phase15Section();

    try requireContains(section, "Primary Linux anchors:");
    try requireContains(section, "- `kernel/sched/core.c`");
    try requireContains(section, "- `mm/page_alloc.c`");
    try requireContains(section, "- `kernel/rcu/tree.c`");
    try requireContains(section, "- `net/core/skbuff.c`");
}

test "phase15 remains ordered after phase14 and before freeze map" {
    try requireBefore(
        roadmap,
        "## Phase 14: Core-Adjacent Bounded Internals",
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    );
    try requireBefore(
        roadmap,
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
        "## Freeze Map for Near- and Mid-Term Planning",
    );
}

test "freeze map repeats phase15 deep-core anchors" {
    const freeze_start = std.mem.indexOf(u8, roadmap, "## Freeze Map for Near- and Mid-Term Planning") orelse unreachable;
    const freeze = roadmap[freeze_start..];

    try requireContains(freeze, "Active freeze-in-C targets for the current product plan:");
    try requireContains(freeze, "- `kernel/sched/core.c`");
    try requireContains(freeze, "- `mm/page_alloc.c`");
    try requireContains(freeze, "- `kernel/rcu/tree.c`");
    try requireContains(freeze, "- `net/core/skbuff.c`");
    try requireContains(freeze, "Boundary-study-only targets before any direct port decision:");
    try requireContains(freeze, "- `kernel/workqueue.c`");
    try requireContains(freeze, "- `kernel/trace/ring_buffer.c`");
}
