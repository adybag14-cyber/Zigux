const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
const phase12_heading = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers";
const phase13_heading = "## Phase 13: Shared Subsystem Helpers";

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn phase12Section() ![]const u8 {
    @setEvalBranchQuota(12_000);
    const start = std.mem.indexOf(u8, roadmap, phase12_heading) orelse return error.MissingPhase12Heading;
    const end = std.mem.indexOfPos(u8, roadmap, start, phase13_heading) orelse return error.MissingPhase13Heading;

    try testing.expect(start < end);
    return roadmap[start..end];
}

test "phase12 complex production driver goal stays high-risk gated" {
    const phase12 = try phase12Section();

    try requireContains(phase12, phase12_heading);
    try requireContains(phase12, "Primary product goal:");
    try requireContains(phase12, "- take on high-value, high-risk drivers only after earlier proof");
}

test "phase12 keeps complex driver and heavy helper anchors explicit" {
    const phase12 = try phase12Section();

    try requireContains(phase12, "Primary Linux anchors:");
    try requireContains(phase12, "- `drivers/net/virtio_net.c`");
    try requireContains(phase12, "- `drivers/nvme/host/pci.c`");
    try requireContains(phase12, "- `drivers/scsi/virtio_scsi.c`");
    try requireContains(phase12, "- `tools/lib/bpf/libbpf.c`");
}

test "phase12 keeps dma queueing recovery and rollout features explicit" {
    const phase12 = try phase12Section();

    try requireContains(phase12, "Required Zigux features:");
    try requireContains(phase12, "- DMA-safe abstractions");
    try requireContains(phase12, "- queueing correctness");
    try requireContains(phase12, "- throughput and recovery parity");
    try requireContains(phase12, "- segmented rollout");
}

test "phase12 destinations and neighboring order stay bounded" {
    const phase12 = try phase12Section();

    try requireContains(phase12, "Recommended Zigux destinations:");
    try requireContains(phase12, "- `drivers/net/virtio_net.zig`");
    try requireContains(phase12, "- `drivers/nvme/host/pci.zig`");
    try requireContains(phase12, "- `drivers/scsi/virtio_scsi.zig`");
    try requireContains(phase12, "- `tools/lib/bpf/zigux_segments/`");

    try requireOrdered("## Phase 11: Simple Production Drivers", phase12_heading);
    try requireOrdered(phase12_heading, phase13_heading);
}

test "phase12 section stays separate from adjacent helper packet" {
    const phase12 = try phase12Section();

    try testing.expect(std.mem.indexOf(u8, phase12, "- filesystem helper wrappers") == null);
    try testing.expect(std.mem.indexOf(u8, phase12, "## Phase 13: Shared Subsystem Helpers") == null);
}
