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

test "phase9 runtime pilot module goal stays test and sample first" {
    try requireContains(roadmap, "## Phase 9: Runtime Pilot Modules");
    try requireContains(roadmap, "Primary product goal:");
    try requireContains(roadmap, "- enter runtime kernels through tests and samples, not production pressure");
}

test "phase9 keeps runtime pilot anchors explicit" {
    try requireContains(roadmap, "Primary Linux anchors:");
    try requireContains(roadmap, "- `lib/atomic64_test.c`");
    try requireContains(roadmap, "- `lib/test_bitmap.c`");
    try requireContains(roadmap, "- `samples/trace_events/trace-events-sample.c`");
    try requireContains(roadmap, "- `samples/kprobes/kretprobe_example.c`");
}

test "phase9 keeps required lifecycle features explicit" {
    try requireContains(roadmap, "Required Zigux features:");
    try requireContains(roadmap, "- first loadable Zigux runtime modules");
    try requireContains(roadmap, "- selftest hooks");
    try requireContains(roadmap, "- runtime module lifecycle parity");
}

test "phase9 destinations and neighboring phase order remain bounded" {
    try requireContains(roadmap, "Recommended Zigux destinations:");
    try requireContains(roadmap, "- `zigux/tests/runtime_*`");
    try requireContains(roadmap, "- `samples/zigux/runtime_*`");

    try requireOrdered("## Phase 8: Userspace-Adjacent Tooling Expansion", "## Phase 9: Runtime Pilot Modules");
    try requireOrdered("## Phase 9: Runtime Pilot Modules", "## Phase 10: Virtio and Lab Drivers");
}
