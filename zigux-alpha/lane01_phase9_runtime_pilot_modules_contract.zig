const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const PhaseWindowError = error{
    MissingStart,
    MissingEnd,
};

fn sectionBetween(comptime start: []const u8, comptime end: []const u8) PhaseWindowError![]const u8 {
    const start_index = std.mem.indexOf(u8, roadmap, start) orelse return error.MissingStart;
    const after_start = roadmap[start_index..];
    const end_index = std.mem.indexOf(u8, after_start[start.len..], end) orelse return error.MissingEnd;
    return after_start[0 .. start.len + end_index];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase9 runtime pilot packet is present and isolated" {
    const phase9 = try sectionBetween(
        "## Phase 9: Runtime Pilot Modules",
        "## Phase 10: Virtio and Lab Drivers",
    );

    try expectContains(phase9, "Primary product goal:");
    try expectContains(phase9, "- enter runtime kernels through tests and samples, not production pressure");
    try expectContains(phase9, "Primary Linux anchors:");
    try expectContains(phase9, "- `lib/atomic64_test.c`");
    try expectContains(phase9, "- `lib/test_bitmap.c`");
    try expectContains(phase9, "- `samples/trace_events/trace-events-sample.c`");
    try expectContains(phase9, "- `samples/kprobes/kretprobe_example.c`");
    try expectNotContains(phase9, "drivers/virtio/virtio.c");
}

test "phase9 required feature packet stays runtime-pilot focused" {
    const phase9 = try sectionBetween(
        "## Phase 9: Runtime Pilot Modules",
        "## Phase 10: Virtio and Lab Drivers",
    );

    try expectContains(phase9, "Required Zigux features:");
    try expectContains(phase9, "- first loadable Zigux runtime modules");
    try expectContains(phase9, "- selftest hooks");
    try expectContains(phase9, "- runtime module lifecycle parity");
    try expectNotContains(phase9, "- virtqueue wrappers");
    try expectNotContains(phase9, "- lab-only driver validation");
}

test "phase9 destinations stay under runtime tests and samples" {
    const phase9 = try sectionBetween(
        "## Phase 9: Runtime Pilot Modules",
        "## Phase 10: Virtio and Lab Drivers",
    );

    try expectContains(phase9, "Recommended Zigux destinations:");
    try expectContains(phase9, "- `zigux/tests/runtime_*`");
    try expectContains(phase9, "- `samples/zigux/runtime_*`");
    try expectNotContains(phase9, "- `drivers/virtio/*.zig`");
}

test "phase9 remains between tooling expansion and virtio lab drivers" {
    const phase8_index = std.mem.indexOf(u8, roadmap, "## Phase 8: Userspace-Adjacent Tooling Expansion") orelse return error.MissingStart;
    const phase9_index = std.mem.indexOf(u8, roadmap, "## Phase 9: Runtime Pilot Modules") orelse return error.MissingStart;
    const phase10_index = std.mem.indexOf(u8, roadmap, "## Phase 10: Virtio and Lab Drivers") orelse return error.MissingEnd;

    try std.testing.expect(phase8_index < phase9_index);
    try std.testing.expect(phase9_index < phase10_index);
}
