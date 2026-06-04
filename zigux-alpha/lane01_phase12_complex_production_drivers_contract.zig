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

test "phase12 complex production driver goal stays high-risk gated" {
    try requireContains(roadmap, "## Phase 12: Complex Production Drivers and Heavy Helper Consumers");
    try requireContains(roadmap, "Primary product goal:");
    try requireContains(roadmap, "- take on high-value, high-risk drivers only after earlier proof");
}

test "phase12 keeps complex driver and heavy helper anchors explicit" {
    try requireContains(roadmap, "Primary Linux anchors:");
    try requireContains(roadmap, "- `drivers/net/virtio_net.c`");
    try requireContains(roadmap, "- `drivers/nvme/host/pci.c`");
    try requireContains(roadmap, "- `drivers/scsi/virtio_scsi.c`");
    try requireContains(roadmap, "- `tools/lib/bpf/libbpf.c`");
}

test "phase12 keeps dma queueing recovery and rollout features explicit" {
    try requireContains(roadmap, "Required Zigux features:");
    try requireContains(roadmap, "- DMA-safe abstractions");
    try requireContains(roadmap, "- queueing correctness");
    try requireContains(roadmap, "- throughput and recovery parity");
    try requireContains(roadmap, "- segmented rollout");
}

test "phase12 destinations and neighboring order stay bounded" {
    try requireContains(roadmap, "Recommended Zigux destinations:");
    try requireContains(roadmap, "- `drivers/net/virtio_net.zig`");
    try requireContains(roadmap, "- `drivers/nvme/host/pci.zig`");
    try requireContains(roadmap, "- `drivers/scsi/virtio_scsi.zig`");
    try requireContains(roadmap, "- `tools/lib/bpf/zigux_segments/`");

    try requireOrdered("## Phase 11: Simple Production Drivers", "## Phase 12: Complex Production Drivers and Heavy Helper Consumers");
    try requireOrdered("## Phase 12: Complex Production Drivers and Heavy Helper Consumers", "## Phase 13: Shared Subsystem Helpers");
}
