const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn sectionBetween(start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, roadmap, start_marker) orelse return error.MissingStartMarker;
    const after_start = roadmap[start_index..];
    const end_offset = std.mem.indexOf(u8, after_start, end_marker) orelse return error.MissingEndMarker;
    return after_start[0..end_offset];
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase12 complex driver packet keeps high value high risk goal" {
    const phase12 = try sectionBetween(
        "## Phase 12: Complex Production Drivers and Heavy Helper Consumers",
        "## Phase 13: Shared Subsystem Helpers",
    );

    try requireContains(phase12, "Primary product goal:");
    try requireContains(phase12, "- take on high-value, high-risk drivers only after earlier proof");
    try requireAbsent(phase12, "touch high-risk drivers before earlier proof");
}

test "phase12 keeps driver and libbpf anchor roster explicit" {
    const phase12 = try sectionBetween(
        "## Phase 12: Complex Production Drivers and Heavy Helper Consumers",
        "## Phase 13: Shared Subsystem Helpers",
    );

    try requireContains(phase12, "Primary Linux anchors:");
    try requireContains(phase12, "- `drivers/net/virtio_net.c`");
    try requireContains(phase12, "- `drivers/nvme/host/pci.c`");
    try requireContains(phase12, "- `drivers/scsi/virtio_scsi.c`");
    try requireContains(phase12, "- `tools/lib/bpf/libbpf.c`");
}

test "phase12 keeps dma queueing throughput and segmented rollout requirements" {
    const phase12 = try sectionBetween(
        "## Phase 12: Complex Production Drivers and Heavy Helper Consumers",
        "## Phase 13: Shared Subsystem Helpers",
    );

    try requireContains(phase12, "Required Zigux features:");
    try requireContains(phase12, "- DMA-safe abstractions");
    try requireContains(phase12, "- queueing correctness");
    try requireContains(phase12, "- throughput and recovery parity");
    try requireContains(phase12, "- segmented rollout");
}

test "phase12 destinations and neighboring phase order stay bounded" {
    const phase12 = try sectionBetween(
        "## Phase 12: Complex Production Drivers and Heavy Helper Consumers",
        "## Phase 13: Shared Subsystem Helpers",
    );

    try requireContains(phase12, "Recommended Zigux destinations:");
    try requireContains(phase12, "- `drivers/net/virtio_net.zig`");
    try requireContains(phase12, "- `drivers/nvme/host/pci.zig`");
    try requireContains(phase12, "- `drivers/scsi/virtio_scsi.zig`");
    try requireContains(phase12, "- `tools/lib/bpf/zigux_segments/`");

    try requireOrdered("## Phase 11: Simple Production Drivers", "## Phase 12: Complex Production Drivers and Heavy Helper Consumers");
    try requireOrdered("## Phase 12: Complex Production Drivers and Heavy Helper Consumers", "## Phase 13: Shared Subsystem Helpers");
}
