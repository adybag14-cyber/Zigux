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

test "phase10 virtio lab driver goal stays vm friendly" {
    try requireContains(roadmap, "## Phase 10: Virtio and Lab Drivers");
    try requireContains(roadmap, "Primary product goal:");
    try requireContains(roadmap, "- prove the driver model on VM-friendly transports before touching harder hardware");
}

test "phase10 keeps virtio anchor roster explicit" {
    try requireContains(roadmap, "Primary Linux anchors:");
    try requireContains(roadmap, "- `drivers/virtio/virtio.c`");
    try requireContains(roadmap, "- `drivers/virtio/virtio_ring.c`");
    try requireContains(roadmap, "- `drivers/virtio/virtio_mmio.c`");
    try requireContains(roadmap, "- `drivers/virtio/virtio_input.c`");
}

test "phase10 keeps wrapper and lab validation features explicit" {
    try requireContains(roadmap, "Required Zigux features:");
    try requireContains(roadmap, "- virtqueue wrappers");
    try requireContains(roadmap, "- MMIO wrappers");
    try requireContains(roadmap, "- lab-only driver validation");
    try requireContains(roadmap, "- dual implementations for risky areas");
}

test "phase10 destinations zar boundary and neighboring order stay bounded" {
    try requireContains(roadmap, "Recommended Zigux destinations:");
    try requireContains(roadmap, "- `drivers/virtio/*.zig`");
    try requireContains(roadmap, "- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified");
    try requireContains(roadmap, "virtio driver and probe experience is relevant as lab methodology and validation design, not as direct Linux product code.");

    try requireOrdered("## Phase 9: Runtime Pilot Modules", "## Phase 10: Virtio and Lab Drivers");
    try requireOrdered("## Phase 10: Virtio and Lab Drivers", "## Phase 11: Simple Production Drivers");
}
