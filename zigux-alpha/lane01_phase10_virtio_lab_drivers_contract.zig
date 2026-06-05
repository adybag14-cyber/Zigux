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

fn phase10Section() ![]const u8 {
    const start_marker = "## Phase 10: Virtio and Lab Drivers";
    const end_marker = "## Phase 11: Simple Production Drivers";
    const start = std.mem.indexOf(u8, roadmap, start_marker) orelse return error.MissingPhase10Start;
    const end = std.mem.indexOfPos(u8, roadmap, start + start_marker.len, end_marker) orelse return error.MissingPhase10End;
    try testing.expect(start < end);
    return roadmap[start..end];
}

test "phase10 virtio lab driver goal stays vm friendly" {
    const phase10 = try phase10Section();

    try requireContains(phase10, "## Phase 10: Virtio and Lab Drivers");
    try requireContains(phase10, "Primary product goal:");
    try requireContains(phase10, "- prove the driver model on VM-friendly transports before touching harder hardware");
}

test "phase10 keeps virtio anchor roster explicit" {
    const phase10 = try phase10Section();

    try requireContains(phase10, "Primary Linux anchors:");
    try requireContains(phase10, "- `drivers/virtio/virtio.c`");
    try requireContains(phase10, "- `drivers/virtio/virtio_ring.c`");
    try requireContains(phase10, "- `drivers/virtio/virtio_mmio.c`");
    try requireContains(phase10, "- `drivers/virtio/virtio_input.c`");
}

test "phase10 keeps wrapper and lab validation features explicit" {
    const phase10 = try phase10Section();

    try requireContains(phase10, "Required Zigux features:");
    try requireContains(phase10, "- virtqueue wrappers");
    try requireContains(phase10, "- MMIO wrappers");
    try requireContains(phase10, "- lab-only driver validation");
    try requireContains(phase10, "- dual implementations for risky areas");
}

test "phase10 destinations zar boundary and neighboring order stay bounded" {
    const phase10 = try phase10Section();

    try requireContains(phase10, "Recommended Zigux destinations:");
    try requireContains(phase10, "- `drivers/virtio/*.zig`");
    try requireContains(phase10, "- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified");
    try requireContains(phase10, "virtio driver and probe experience is relevant as lab methodology and validation design, not as direct Linux product code.");

    try requireOrdered("## Phase 9: Runtime Pilot Modules", "## Phase 10: Virtio and Lab Drivers");
    try requireOrdered("## Phase 10: Virtio and Lab Drivers", "## Phase 11: Simple Production Drivers");
}
